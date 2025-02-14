from django.shortcuts import render
import time
import random
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.http import Http404
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from doctors.models import Doctor
from patients.models import Patient
from .token_builder import RtcTokenBuilder
from .models import VideoCall
from .serializers import VideoCallSerializer, TokenSerializer, TokenRequestSerializer

logger = logging.getLogger(__name__)

# Constants for token expiration (in seconds)
TOKEN_EXPIRATION_IN_SECONDS = 3600  # 1 hour
JOIN_CHANNEL_PRIVILEGE_EXPIRATION_IN_SECONDS = 3600  # 1 hour
PUB_AUDIO_PRIVILEGE_EXPIRATION_IN_SECONDS = 3600  # 1 hour
PUB_VIDEO_PRIVILEGE_EXPIRATION_IN_SECONDS = 3600  # 1 hour
PUB_DATA_STREAM_PRIVILEGE_EXPIRATION_IN_SECONDS = 3600  # 1 hour

# Role constants from Agora SDK
Role_Publisher = 1  # Host
Role_Subscriber = 2

def generate_agora_rtc_token(channel_name, uid):
    """
    Generate an Agora RTC token using our custom token builder.
    
    Args:
        channel_name (str): The name of the channel to join
        uid (int): The user ID for the token
        
    Returns:
        tuple: (token string, expiration timestamp)
    """
    try:
        # Validate channel name
        if not isinstance(channel_name, str) or len(channel_name) < 3:
            raise ValueError("Channel name must be a string of at least 3 characters")
        
        # Validate UID
        if not isinstance(uid, int) or uid < 1:
            raise ValueError("UID must be a positive integer")
            
        # Get current timestamp
        current_timestamp = int(time.time())
        
        # Calculate privilege expire time (24 hours from now)
        privilegeExpiredTs = current_timestamp + TOKEN_EXPIRATION_IN_SECONDS
        
        # Build token using our custom token builder
        token = RtcTokenBuilder.build_token_with_uid(
            settings.AGORA_APP_ID,
            settings.AGORA_APP_CERTIFICATE,
            channel_name,
            uid,
            Role_Publisher,  # Always use publisher role for video calls
            privilegeExpiredTs
        )
        
        logger.info(f"Generated Agora token for channel: {channel_name}, uid: {uid}, expiry: {privilegeExpiredTs}")
        return token, privilegeExpiredTs
        
    except Exception as e:
        logger.error(f"Failed to generate Agora token: {str(e)}")
        raise Exception(f"Token generation failed: {str(e)}")

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_agora_token(request):
    """
    Generate an Agora token for video calls based on appointment details.
    Required parameters:
    - doctor_id: UUID of the doctor
    - slot_time: Appointment slot time
    """
    try:
        # Extract required parameters
        doctor_id = request.data.get('doctor_id')
        slot_time = request.data.get('slot_time')

        if not doctor_id or not slot_time:
            return Response({
                'error': 'Missing required parameters: doctor_id and slot_time are required'
            }, status=400)

        # Create a unique channel name based on doctor_id and slot_time
        # Remove special characters and spaces from slot_time to create a valid channel name
        cleaned_slot_time = ''.join(e for e in slot_time if e.isalnum())
        channel_name = f"vid_{doctor_id}_{cleaned_slot_time}"

        # Generate a unique uid based on timestamp and random number
        timestamp_part = int(str(int(time.time()))[-4:])  # Last 4 digits of timestamp
        random_part = random.randint(1, 999)
        uid = int(f"{timestamp_part}{random_part}")  # Combine for unique ID

        # Generate token using the helper function
        token, expiration_time = generate_agora_rtc_token(channel_name, uid)

        response_data = {
            'token': token,
            'channel_name': channel_name,
            'uid': uid,
            'app_id': settings.AGORA_APP_ID,
            'expiration_time': datetime.fromtimestamp(expiration_time),
            'role': Role_Publisher
        }

        logger.info(f"Generated token response: {response_data}")
        return Response(response_data)

    except Exception as e:
        logger.error(f"Token generation failed: {str(e)}", exc_info=True)
        return Response({'error': f'Failed to generate video token: {str(e)}'}, status=400)

@api_view(['POST'])
def refresh_agora_token(request):
    """Refresh an existing Agora token"""
    
    serializer = TokenRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'status': 'error', 'errors': serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        channel_name = serializer.validated_data['channel_name']
        uid = serializer.validated_data.get('uid', random.randint(1, 230))
        
        # Generate new token using the helper function
        token, expiration_time = generate_agora_rtc_token(channel_name, uid)
        
        return Response({
            'status': 'success',
            'data': {
                'token': token,
                'channel': channel_name,
                'uid': uid,
                'role': Role_Publisher,
                'app_id': settings.AGORA_APP_ID,
                'expiration_time': datetime.fromtimestamp(expiration_time)
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to refresh Agora token: {str(e)}", exc_info=True)
        return Response(
            {'status': 'error', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class VideoCallViewSet(viewsets.ModelViewSet):
    queryset = VideoCall.objects.all()
    serializer_class = VideoCallSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied("Authentication required")

        # Get doctor and patient profiles by email
        try:
            doctor = Doctor.objects.get(email=user.email)
            return VideoCall.objects.filter(doctor=doctor)
        except Doctor.DoesNotExist:
            try:
                patient = Patient.objects.get(email=user.email)
                return VideoCall.objects.filter(patient=patient)
            except Patient.DoesNotExist:
                raise PermissionDenied("User must be either a doctor or a patient")

    def get_object(self):
        try:
            obj = super().get_object()
            user = self.request.user

            # Check if user is either the doctor or patient of this call
            try:
                doctor = Doctor.objects.get(email=user.email)
                if obj.doctor == doctor:
                    return obj
            except Doctor.DoesNotExist:
                try:
                    patient = Patient.objects.get(email=user.email)
                    if obj.patient == patient:
                        return obj
                except Patient.DoesNotExist:
                    pass

            raise PermissionDenied("You do not have permission to access this video call")
        except (Http404, NotFound):
            raise PermissionDenied("Video call not found or you do not have permission to access it")

    def perform_create(self, serializer):
        # Generate a unique channel name
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        channel_name = f"call_{timestamp}_{random_suffix}"
        
        # Ensure channel name is unique
        while VideoCall.objects.filter(channel_name=channel_name).exists():
            random_suffix = random.randint(1000, 9999)
            channel_name = f"call_{timestamp}_{random_suffix}"
        
        try:
            # Validate channel name with Agora service
            AgoraService.validate_channel(channel_name)
            
            serializer.save(channel_name=channel_name)
            logger.info(f"Created video call with channel name: {channel_name}")
        except Exception as e:
            logger.error(f"Failed to create video call: {str(e)}")
            raise ValidationError(str(e))

    def get_user_role(self, video_call):
        """Get the user's role in the video call"""
        user = self.request.user
        logger.debug(f"Checking role for user {user.email}")
        
        try:
            doctor = Doctor.objects.get(email=user.email)
            logger.debug(f"Found doctor: {doctor.name}")
            if doctor == video_call.doctor:
                logger.debug("User is the doctor for this call")
                return 'doctor'
        except Doctor.DoesNotExist:
            logger.debug("User is not a doctor")
            pass

        try:
            patient = Patient.objects.get(email=user.email)
            logger.debug(f"Found patient: {patient.name}")
            if patient == video_call.patient:
                logger.debug("User is the patient for this call")
                return 'patient'
        except Patient.DoesNotExist:
            logger.debug("User is not a patient")
            pass

        logger.debug("User has no role in this call")
        return None

    def check_call_permissions(self, video_call):
        """Check if the current user has permission to access the call"""
        role = self.get_user_role(video_call)
        if not role:
            raise PermissionDenied("You are not authorized to access this call")
        return role

    @action(detail=True, methods=['post'], url_path='join', url_name='join')
    def join(self, request, pk=None):
        try:
            logger.debug(f"Join request for call {pk} from user {request.user.email}")
            video_call = self.get_object()
            role = self.check_call_permissions(video_call)
            logger.debug(f"User role: {role}")
            
            # Check if call can be joined
            can_join, error_message = video_call.can_join()
            if not can_join:
                raise ValidationError(error_message)
            
            # Generate Agora token
            try:
                # Generate a unique user ID for this session
                uid = random.randint(1, 230)
                token, expiration_time = generate_agora_rtc_token(
                    video_call.channel_name,
                    uid
                )
            except Exception as e:
                logger.error(f"Failed to generate Agora token: {str(e)}")
                raise ValidationError(f"Failed to generate video call token: {str(e)}")

            # Start the call if it's the first person joining
            if video_call.status == 'scheduled':
                video_call.start_call()
                logger.debug("Call status updated to ongoing")

            response_data = {
                'channel_name': video_call.channel_name,
                'token': token,
                'uid': uid,
                'expiration_time': datetime.fromtimestamp(expiration_time),
                'call_duration': video_call.get_duration(),
                'app_id': settings.AGORA_APP_ID
            }
            
            return Response(
                TokenSerializer(response_data).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Failed to join call: {str(e)}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='end', url_name='end')
    def end(self, request, pk=None):
        try:
            logger.debug(f"End request for call {pk} from user {request.user.email}")
            video_call = self.get_object()
            role = self.check_call_permissions(video_call)
            logger.debug(f"User role: {role}")
            
            if not video_call.mark_completed():
                raise ValidationError("Call cannot be ended (not ongoing)")

            response_data = VideoCallSerializer(video_call).data
            response_data['duration'] = video_call.get_duration()
            
            logger.debug("Call ended successfully")
            return Response(response_data, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            logger.warning(f"Permission denied: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except VideoCall.DoesNotExist:
            logger.warning(f"Video call not found: {pk}")
            return Response(
                {"error": "Video call not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Failed to end call: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='cancel', url_name='cancel')
    def cancel(self, request, pk=None):
        """Cancel a scheduled call"""
        try:
            logger.debug(f"Cancel request for call {pk} from user {request.user.email}")
            video_call = self.get_object()
            role = self.check_call_permissions(video_call)
            logger.debug(f"User role: {role}")
            
            if not video_call.mark_cancelled():
                raise ValidationError("Call cannot be cancelled (not in scheduled status)")

            logger.debug("Call cancelled successfully")
            return Response(
                VideoCallSerializer(video_call).data,
                status=status.HTTP_200_OK
            )
        except PermissionDenied as e:
            logger.warning(f"Permission denied: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except VideoCall.DoesNotExist:
            logger.warning(f"Video call not found: {pk}")
            return Response(
                {"error": "Video call not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Failed to cancel call: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
