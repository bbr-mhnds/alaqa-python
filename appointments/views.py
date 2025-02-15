from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
import logging
from django.utils import timezone
from django.db import transaction
from .models import Appointment, Doctor
from .serializers import AppointmentSerializer, AppointmentCompletionSerializer
from .permissions import IsAppointmentDoctor
from datetime import timedelta
from rest_framework import serializers
from services.email_service import EmailService
from otp.services import OTPService

logger = logging.getLogger(__name__)

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()
    
    def get_permissions(self):
        if self.action in ["create", "list"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Create a new appointment with video token generation and notifications.
        """
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                appointment = serializer.save()
                
                # Send notifications to doctor
                self._send_doctor_notifications(appointment)
                
                # Log successful appointment creation with video token
                logger.info(
                    f"Created appointment {appointment.id} for doctor {appointment.doctor.id} "
                    f"with video token at {appointment.slot_time}"
                )
                
                return Response(
                    {
                        'status': 'success',
                        'message': 'Appointment created successfully',
                        'data': serializer.data
                    }, 
                    status=status.HTTP_201_CREATED
                )
                
        except serializers.ValidationError as e:
            logger.warning(f"Validation error in appointment creation: {str(e)}")
            return Response(
                {
                    'status': 'error',
                    'message': 'Invalid appointment data',
                    'errors': e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Appointment creation failed: {str(e)}", exc_info=True)
            return Response(
                {
                    'status': 'error',
                    'message': 'Failed to create appointment',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_doctor_notifications(self, appointment):
        """
        Send email and SMS notifications to the doctor about the new appointment.
        """
        try:
            doctor = appointment.doctor
            slot_time = appointment.slot_time.strftime("%Y-%m-%d %H:%M")
            duration = appointment.duration
            
            # Send email using enterprise template
            email_service = EmailService()
            email_result = email_service.send_appointment_notification(
                to_email=doctor.email,
                doctor_name=doctor.name,
                doctor_name_arabic=doctor.name_arabic,
                slot_time=slot_time,
                duration=duration,
                phone_number=appointment.phone_number,
                language=appointment.language
            )
            
            if not email_result['success']:
                logger.error(f"Failed to send email to doctor {doctor.email}: {email_result['message']}")
            
            # Prepare SMS content (bilingual and concise)
            sms_content = f"""ALAQA: New appointment scheduled for {slot_time}. Duration: {duration}min.
موعد جديد في {slot_time}. المدة: {duration} دقيقة"""
            
            # Send SMS
            sms_result = OTPService.send_sms(doctor.phone, sms_content)
            
            if not sms_result[0]:  # sms_result returns (success, message)
                logger.error(f"Failed to send SMS to doctor {doctor.phone}: {sms_result[1]}")
                
        except Exception as e:
            logger.error(f"Failed to send notifications: {str(e)}", exc_info=True)
            # Don't raise the exception to prevent appointment creation from failing
            
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # If user is authenticated and is a doctor, only show their appointments
        if self.request.user.is_authenticated:
            try:
                doctor = Doctor.objects.get(email=self.request.user.email)
                return queryset.filter(doctor=doctor)
            except Doctor.DoesNotExist:
                pass
        
        # For unauthenticated users or non-doctors, filter by doctor_id if provided
        doctor_id = self.request.query_params.get("doctor_id")
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
            
        # Filter by status if provided
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        return queryset

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = "CANCELLED"
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_appointment(request, appointment_id):
    """
    Complete an appointment with validation and proper error handling.
    Only the assigned doctor can complete their scheduled appointments.
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response(
            {
                'status': 'error',
                'message': 'Appointment not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if the user is the assigned doctor
    if appointment.doctor.email != request.user.email:
        return Response(
            {
                'status': 'error',
                'message': 'You are not authorized to complete this appointment'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Validate appointment state
    if appointment.status != 'SCHEDULED':
        return Response(
            {
                'status': 'error',
                'message': f'Cannot complete appointment in {appointment.status} state'
            },
            status=status.HTTP_409_CONFLICT
        )

    serializer = AppointmentCompletionSerializer(data=request.data)
    if not serializer.is_valid():
        # Get the first error message
        if 'duration_minutes' in serializer.errors:
            error_message = "Duration minutes must be greater than 0"
        elif 'non_field_errors' in serializer.errors:
            error_message = serializer.errors['non_field_errors'][0]
        else:
            error_message = next(iter(serializer.errors.values()))[0]
            
        return Response(
            {
                'status': 'error',
                'message': error_message,
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get validated data, using None for missing fields
    completion_time = serializer.validated_data.get('completion_time')
    duration_minutes = serializer.validated_data.get('duration_minutes')
    completion_notes = serializer.validated_data.get('completion_notes')

    # Set default completion time if not provided
    if completion_time is None:
        completion_time = timezone.now()

    # Additional validations for completion time if provided in request
    if 'completion_time' in request.data:
        current_time = timezone.now()
        
        # Check if completion time is before scheduled time
        if completion_time < appointment.slot_time:
            return Response(
                {
                    'status': 'error',
                    'message': 'Completion time must be after scheduled time'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # For appointments in the past or present
        if appointment.slot_time <= current_time:
            # Check if completion time is in the future
            if completion_time > current_time:
                return Response(
                    {
                        'status': 'error',
                        'message': 'Completion time cannot be in the future'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        # For appointments in the future
        else:
            # Check if completion time is too far after scheduled time
            if completion_time > appointment.slot_time + timedelta(hours=2):
                return Response(
                    {
                        'status': 'error',
                        'message': 'Completion time cannot be in the future'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

    try:
        with transaction.atomic():
            # Update appointment with only provided fields
            appointment.status = 'COMPLETED'
            appointment.completion_time = completion_time
            
            if duration_minutes is not None:
                appointment.duration_minutes = duration_minutes
                
            if completion_notes is not None:
                appointment.completion_notes = completion_notes
                
            appointment.save()

            # Serialize the response
            response_serializer = AppointmentSerializer(appointment)
            
            # TODO: Add notification logic here
            # notify_patient_appointment_completed(appointment)
            
            return Response(
                {
                    'status': 'success',
                    'data': response_serializer.data
                },
                status=status.HTTP_200_OK
            )

    except Exception as e:
        logger.error(f"Failed to complete appointment: {str(e)}")
        return Response(
            {
                'status': 'error',
                'message': 'Failed to complete appointment',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )