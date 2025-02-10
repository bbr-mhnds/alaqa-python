from django.shortcuts import render
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters import rest_framework as django_filters
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
from .models import Doctor, DoctorVerification, DoctorBankDetails, DoctorSchedule, PriceCategory
from .serializers import (
    DoctorSerializer, 
    DoctorStatusSerializer,
    DoctorRegistrationSerializer,
    DoctorApprovalSerializer,
    DoctorBankDetailsSerializer,
    DoctorScheduleSerializer,
    PriceCategorySerializer,
    DoctorRegistrationInitiateSerializer,
    DoctorRegistrationVerifySerializer
)
from rest_framework import serializers
from .services import DoctorVerificationService
import logging
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.db import transaction
from rest_framework.throttling import AnonRateThrottle

logger = logging.getLogger(__name__)

class RegistrationRateThrottle(AnonRateThrottle):
    rate = '100/hour'  # Increased for testing
    
class VerificationRateThrottle(AnonRateThrottle):
    rate = '100/hour'  # Increased for testing

class DoctorFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status')
    specialty = django_filters.UUIDFilter(field_name='specialities__id')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Doctor
        fields = ['status', 'specialty']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(name_arabic__icontains=value) |
            models.Q(email__icontains=value)
        )

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    filterset_class = DoctorFilter
    filter_backends = [django_filters.DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        List and Retrieve endpoints are public
        Other actions require authentication
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter queryset based on action and user permissions
        Public endpoints only see approved doctors
        """
        queryset = super().get_queryset()
        
        # For public endpoints (list, retrieve), only show approved doctors if not authenticated
        if self.action in ['list', 'retrieve'] and not self.request.user.is_authenticated:
            queryset = queryset.filter(status='approved')
        
        return queryset.order_by(self.ordering[0])

    def list(self, request, *args, **kwargs):
        """
        List doctors with pagination and filtering
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response({
                    'status': 'success',
                    'data': {
                        'doctors': serializer.data,
                        'pagination': {
                            'total': self.paginator.page.paginator.count,
                            'pages': self.paginator.page.paginator.num_pages,
                            'page': self.paginator.page.number,
                            'limit': self.paginator.page_size
                        }
                    }
                })

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'data': {
                    'doctors': serializer.data
                }
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single doctor
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'status': 'success',
                'data': {
                    'doctor': serializer.data
                }
            })
        except ObjectDoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Doctor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        """
        Create a new doctor
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                'status': 'success',
                'message': 'Doctor created successfully',
                'data': {
                    'doctor': serializer.data
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Update a doctor
        """
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            try:
                serializer.is_valid(raise_exception=True)
            except serializers.ValidationError as e:
                return Response({
                    'status': 'error',
                    'message': 'Validation error',
                    'errors': e.detail
                }, status=status.HTTP_400_BAD_REQUEST)
                
            self.perform_update(serializer)
            return Response({
                'status': 'success',
                'message': 'Doctor updated successfully',
                'data': {
                    'doctor': serializer.data
                }
            })
        except ObjectDoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Doctor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a doctor
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                'status': 'success',
                'message': 'Doctor deleted successfully'
            }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Doctor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        try:
            instance = self.get_object()
            serializer = DoctorStatusSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Doctor status updated successfully',
                'data': {
                    'doctor': serializer.data
                }
            })
        except ObjectDoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Doctor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class IsSuperAdmin(permissions.BasePermission):
    """Custom permission to only allow super admins to approve/reject doctors"""
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class DoctorRegistrationViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorRegistrationSerializer
    authentication_classes = []  # Disable authentication completely
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post']
    
    def get_throttles(self):
        if self.action == 'initiate':
            return [RegistrationRateThrottle()]
        elif self.action == 'verify':
            return [VerificationRateThrottle()]
        return []

    def get_serializer_class(self):
        if self.action == 'initiate':
            return DoctorRegistrationInitiateSerializer
        elif self.action == 'verify':
            return DoctorRegistrationVerifySerializer
        return DoctorRegistrationSerializer

    @action(detail=False, methods=['post'], authentication_classes=[], permission_classes=[permissions.AllowAny])
    def initiate(self, request):
        """Step 1: Complete registration with full doctor details"""
        try:
            # Validate registration data
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            validated_data = serializer.validated_data
            email = validated_data['email']
            phone = validated_data['phone']
            
            # Create doctor instance with all data
            with transaction.atomic():
                # Create doctor
                doctor = Doctor.objects.create(
                    name=validated_data['name'],
                    name_arabic=validated_data['name_arabic'],
                    sex=validated_data['sex'],
                    email=email,
                    phone=phone,
                    experience=validated_data['experience'],
                    category=validated_data['category'],
                    language_in_sessions=validated_data['language_in_sessions'],
                    license_number=validated_data['license_number'],
                    profile_arabic=validated_data['profile_arabic'],
                    profile_english=validated_data['profile_english'],
                    status='pending',
                    terms_and_privacy_accepted=validated_data['terms_and_privacy_accepted']
                )

                # Handle file uploads
                if 'license_document' in request.FILES:
                    doctor.license_document = request.FILES['license_document']
                if 'qualification_document' in request.FILES:
                    doctor.qualification_document = request.FILES['qualification_document']
                if 'additional_documents' in request.FILES:
                    doctor.additional_documents = request.FILES['additional_documents']
                if 'photo' in request.FILES:
                    doctor.photo = request.FILES['photo']
                
                doctor.save()

                # Add specialities
                doctor.specialities.set(validated_data['specialities'])

                # Create user account
                from django.contrib.auth import get_user_model
                from django.contrib.auth.models import Group
                User = get_user_model()
                
                user = User.objects.create_user(
                    email=email,
                    password=validated_data['password'],
                    is_active=False,  # Will be activated upon approval
                    is_staff=True  # Doctors need admin panel access
                )
                
                # Add doctor role
                doctor_group, _ = Group.objects.get_or_create(name='Doctors')
                user.groups.add(doctor_group)

                # Send verification codes
                verification_result = DoctorVerificationService.send_verification_codes(
                    email=email,
                    phone=phone,
                    registration_data={}  # Empty since we've already saved the data
                )
                
                return Response({
                    'status': 'success',
                    'message': 'Registration initiated successfully. Please verify your phone number.',
                    'data': {
                        'verification_id': str(verification_result['verification_id']),
                        'doctor_id': str(doctor.id),
                        'next_steps': [
                            'Check your phone for the verification code.',
                            'Use the code to verify your phone number.',
                            'Your profile will be reviewed by our team after verification.',
                            'You will receive a notification once your account is approved.'
                        ]
                    }
                })
                
        except serializers.ValidationError as e:
            return Response({
                'status': 'error',
                'message': 'Validation error',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], authentication_classes=[], permission_classes=[permissions.AllowAny])
    def verify(self, request):
        """Step 2: Verify OTP code"""
        try:
            logger.info(f"[DOCTOR_DEBUG] Starting verification process for email: {request.data.get('email')}")
            
            # Extract verification data
            verification_data = {
                'verification_id': request.data.get('verification_id'),
                'email': request.data.get('email'),
                'sms_code': request.data.get('sms_code')
            }
            
            # Log verification attempt
            logger.info(f"[DOCTOR_DEBUG] Verification attempt - Data: {verification_data}")
            
            # Validate verification data
            verify_serializer = DoctorRegistrationVerifySerializer(data=verification_data)
            verify_serializer.is_valid(raise_exception=True)
            
            verification = verify_serializer.validated_data['verification']
            otp = verify_serializer.validated_data['otp']
            
            logger.info(f"[DOCTOR_DEBUG] Found verification record - ID: {verification.id}")
            logger.info(f"[DOCTOR_DEBUG] Found OTP record - ID: {otp.id}, Attempts: {otp.attempts}")
            
            # Verify OTP code
            if verification_data['sms_code'] == otp.otp_code:
                logger.info("[DOCTOR_DEBUG] OTP code matched")
                
                # Use transaction to ensure atomic operations
                with transaction.atomic():
                    # Mark OTP as verified
                    otp.is_verified = True
                    otp.save()
                    logger.info(f"[DOCTOR_DEBUG] Marked OTP as verified - ID: {otp.id}")
                    
                    # Mark verification as complete
                    verification.phone_verified = True
                    verification.save()
                    logger.info(f"[DOCTOR_DEBUG] Marked verification as complete - ID: {verification.id}")

                    # Create user account
                    from django.contrib.auth import get_user_model
                    from django.contrib.auth.models import Group
                    User = get_user_model()
                    
                    # Create user with a temporary password
                    temp_password = User.objects.make_random_password()
                    user = User.objects.create_user(
                        email=verification.email,
                        password=temp_password,
                        is_active=True,
                        is_staff=True
                    )
                    
                    # Add to doctors group
                    doctor_group, _ = Group.objects.get_or_create(name='Doctors')
                    user.groups.add(doctor_group)
                    logger.info(f"[DOCTOR_DEBUG] Created user account - ID: {user.id}")

                    # Create doctor profile
                    from .models import Doctor
                    doctor = Doctor.objects.create(
                        name=f"Dr. {verification.email.split('@')[0]}",  # Temporary name
                        name_arabic="طبيب",  # Temporary name
                        email=verification.email,
                        phone=verification.phone,
                        status='pending',
                        category='general'  # Default category
                    )
                    logger.info(f"[DOCTOR_DEBUG] Created doctor profile - ID: {doctor.id}")
                    
                    return Response({
                        'status': 'success',
                        'message': 'Phone number verified and account created successfully.',
                        'data': {
                            'verification_id': str(verification.id),
                            'doctor_id': str(doctor.id),
                            'next_steps': [
                                'Your phone number has been verified.',
                                'Your account has been created.',
                                'Please complete your profile with additional details.'
                            ]
                        }
                    })
            else:
                # Increment OTP attempts
                otp.attempts += 1
                otp.save()
                
                logger.warning(f"[DOCTOR_DEBUG] Invalid OTP code provided - Attempts: {otp.attempts}")
                
                return Response({
                    'status': 'error',
                    'message': 'Invalid verification code',
                    'data': {
                        'attempts_remaining': max(3 - otp.attempts, 0)
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except serializers.ValidationError as e:
            logger.error(f"[DOCTOR_DEBUG] Verification validation error: {str(e)}")
            logger.error(f"[DOCTOR_DEBUG] Validation error details: {e.detail}")
            return Response({
                'status': 'error',
                'message': 'Validation error',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"[DOCTOR_DEBUG] Verification error: {str(e)}", exc_info=True)
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], authentication_classes=[], permission_classes=[permissions.AllowAny])
    def complete_registration(self, request):
        """Step 3: Complete registration with full doctor details"""
        try:
            verification_id = request.data.get('verification_id')
            email = request.data.get('email')
            
            logger.info(f"[DOCTOR_DEBUG] Starting complete registration for email: {email}")
            
            try:
                verification = DoctorVerification.objects.get(
                    id=verification_id,
                    email=email,
                    phone_verified=True,
                    is_used=False
                )
            except DoctorVerification.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Invalid or unverified verification ID',
                    'errors': {
                        'verification_id': ['Please verify your phone number first']
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get existing doctor
            try:
                doctor = Doctor.objects.get(email=email)
            except Doctor.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Doctor profile not found. Please verify your phone number first.',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update registration data
            registration_data = request.data.copy()
            registration_data.pop('verification_id', None)
            
            # Handle file uploads
            if 'license_document' in request.FILES:
                logger.info("[DOCTOR_DEBUG] Processing license document")
                registration_data['license_document'] = request.FILES['license_document']
            if 'qualification_document' in request.FILES:
                logger.info("[DOCTOR_DEBUG] Processing qualification document")
                registration_data['qualification_document'] = request.FILES['qualification_document']
            if 'additional_documents' in request.FILES:
                logger.info("[DOCTOR_DEBUG] Processing additional documents")
                registration_data['additional_documents'] = request.FILES['additional_documents']
            
            # Update doctor profile
            logger.info("[DOCTOR_DEBUG] Validating registration data")
            registration_serializer = DoctorRegistrationSerializer(doctor, data=registration_data, partial=True)
            registration_serializer.is_valid(raise_exception=True)
            
            with transaction.atomic():
                logger.info("[DOCTOR_DEBUG] Updating doctor record")
                doctor = registration_serializer.save()
                logger.info(f"[DOCTOR_DEBUG] Doctor record updated successfully - ID: {doctor.id}")
                
                # Update user password if provided
                if 'password' in registration_data:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(email=email)
                    user.set_password(registration_data['password'])
                    user.save()
                    logger.info(f"[DOCTOR_DEBUG] Updated user password")
                
                # Mark verification as used
                verification.is_used = True
                verification.save()
                
                return Response({
                    'status': 'success',
                    'message': 'Registration completed successfully. Your profile is pending approval.',
                    'data': {
                        'doctor': DoctorSerializer(doctor).data,
                        'next_steps': [
                            'Your profile is being reviewed by our team.',
                            'You will receive a notification once your account is approved.',
                            'After approval, you can sign in using your email and password.',
                            'For any questions, please contact our support team.'
                        ]
                    }
                }, status=status.HTTP_200_OK)
                
        except serializers.ValidationError as e:
            logger.error(f"[DOCTOR_DEBUG] Registration validation error: {str(e)}")
            logger.error(f"[DOCTOR_DEBUG] Validation error details: {e.detail}")
            return Response({
                'status': 'error',
                'message': 'Validation error',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"[DOCTOR_DEBUG] Registration error: {str(e)}", exc_info=True)
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """Deprecated: Use initiate and verify endpoints instead"""
        return Response({
            'status': 'error',
            'message': 'Please use /api/v1/doctors/register/initiate/ to start registration'
        }, status=status.HTTP_400_BAD_REQUEST)

class DoctorApprovalViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.filter(status='pending')
    serializer_class = DoctorApprovalSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    http_method_names = ['get', 'patch']  # Only allow GET and PATCH methods

    def get_queryset(self):
        """Filter doctors based on status query param"""
        queryset = Doctor.objects.all()
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        doctor = serializer.save()

        # Send notification to doctor about approval/rejection
        if doctor.status == 'approved':
            # TODO: Send approval notification
            message = 'Doctor approved successfully'
        else:
            # TODO: Send rejection notification with reason
            message = 'Doctor rejected successfully'

        return Response({
            'status': 'success',
            'message': message,
            'data': DoctorSerializer(doctor).data
        })

class DoctorBankDetailsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing doctor bank details
    """
    serializer_class = DoctorBankDetailsSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        """
        Filter queryset to only show bank details for the specified doctor
        """
        doctor_email = self.kwargs.get('doctor_email')
        return DoctorBankDetails.objects.filter(doctor__email=doctor_email)

    def create(self, request, *args, **kwargs):
        """
        Create new bank details for a doctor
        """
        try:
            doctor_email = self.kwargs.get('doctor_email')
            doctor = Doctor.objects.get(email=doctor_email)
            
            # Add doctor to request data
            mutable_data = request.data.copy()
            mutable_data['doctor'] = doctor.id
            
            serializer = self.get_serializer(data=mutable_data)
            serializer.is_valid(raise_exception=True)
            
            # Deactivate existing bank details
            DoctorBankDetails.objects.filter(doctor=doctor, is_active=True).update(is_active=False)
            
            # Save new bank details
            serializer.save(doctor=doctor)
            
            return Response({
                'status': 'success',
                'message': 'Bank details added successfully',
                'data': {
                    'bank_details': serializer.data
                }
            }, status=status.HTTP_201_CREATED)
            
        except Doctor.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Doctor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except serializers.ValidationError as e:
            return Response({
                'status': 'error',
                'message': 'Validation error',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """
        List bank details for a specific doctor
        """
        try:
            queryset = self.get_queryset().filter(is_active=True)
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'data': {
                    'bank_details': serializer.data
                }
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Update bank details
        """
        try:
            instance = self.get_object()
            partial = kwargs.pop('partial', False)
            
            serializer = self.get_serializer(
                instance, 
                data=request.data, 
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response({
                'status': 'success',
                'message': 'Bank details updated successfully',
                'data': {
                    'bank_details': serializer.data
                }
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class DoctorScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing doctor schedules
    """
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        """
        Filter queryset to only show schedules for the specified doctor
        """
        doctor_email = self.kwargs.get('doctor_email')
        return DoctorSchedule.objects.filter(doctor__email=doctor_email)

    def list(self, request, *args, **kwargs):
        """
        List schedules for a specific doctor
        """
        try:
            doctor_email = self.kwargs.get('doctor_email')
            doctor = Doctor.objects.get(email=doctor_email)
            
            # Get or create schedules for all days
            schedules = []
            for day, _ in DoctorSchedule.DAYS_OF_WEEK:
                schedule, created = DoctorSchedule.objects.get_or_create(
                    doctor=doctor,
                    day=day,
                    defaults={'is_available': False}
                )
                schedules.append(schedule)
            
            serializer = self.get_serializer(schedules, many=True)
            return Response({
                'status': 'success',
                'data': {
                    'schedules': serializer.data
                }
            })
        except Doctor.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Doctor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """
        Create or update schedules for a doctor
        """
        try:
            doctor_email = self.kwargs.get('doctor_email')
            doctor = Doctor.objects.get(email=doctor_email)
            
            schedules_data = request.data.get('schedules', [])
            if not schedules_data:
                raise serializers.ValidationError({
                    'schedules': ['Schedule data is required']
                })

            # Validate and update each schedule
            updated_schedules = []
            for schedule_data in schedules_data:
                day = schedule_data.get('day')
                if not day:
                    raise serializers.ValidationError({
                        'day': ['Day is required for each schedule']
                    })

                schedule, created = DoctorSchedule.objects.get_or_create(
                    doctor=doctor,
                    day=day
                )

                serializer = self.get_serializer(
                    schedule,
                    data=schedule_data,
                    partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                updated_schedules.append(schedule)

            # Return all schedules, including those not updated
            all_schedules = DoctorSchedule.objects.filter(doctor=doctor)
            serializer = self.get_serializer(all_schedules, many=True)

            return Response({
                'status': 'success',
                'message': 'Working hours updated successfully',
                'data': {
                    'schedules': serializer.data
                }
            }, status=status.HTTP_200_OK)

        except Doctor.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Doctor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except serializers.ValidationError as e:
            return Response({
                'status': 'error',
                'message': 'Validation error',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class DoctorPriceCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing doctor price categories and their duration-based prices
    """
    serializer_class = PriceCategorySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        doctor_email = self.kwargs.get('doctor_email')
        return PriceCategory.objects.filter(doctor__email=doctor_email)

    def list(self, request, *args, **kwargs):
        try:
            doctor = Doctor.objects.get(email=self.kwargs.get('doctor_email'))
            queryset = self.get_queryset()
            categories_data = self.get_serializer(queryset, many=True).data
            
            # Include appointment settings in response
            response_data = {
                'categories': categories_data,
                'accept_instant_appointment': doctor.accept_instant_appointment,
                'accept_tamkeen_clinics': doctor.accept_tamkeen_clinics
            }
            return Response(response_data)
        except Doctor.DoesNotExist:
            return Response(
                {'detail': 'Doctor not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        try:
            doctor = Doctor.objects.get(email=self.kwargs.get('doctor_email'))
            
            # Update appointment settings if provided
            if 'accept_instant_appointment' in request.data:
                doctor.accept_instant_appointment = request.data.get('accept_instant_appointment')
            if 'accept_tamkeen_clinics' in request.data:
                doctor.accept_tamkeen_clinics = request.data.get('accept_tamkeen_clinics')
            doctor.save()
            
            # Handle categories
            if 'categories' in request.data:
                categories_data = request.data.get('categories', [])
                created_categories = []
                
                for category_data in categories_data:
                    # Check if category type already exists
                    existing = PriceCategory.objects.filter(
                        doctor=doctor,
                        type=category_data.get('type')
                    ).first()
                    
                    if existing:
                        # Update existing category
                        serializer = self.get_serializer(
                            existing,
                            data=category_data,
                            partial=True
                        )
                    else:
                        # Create new category
                        serializer = self.get_serializer(data=category_data)
                    
                    serializer.is_valid(raise_exception=True)
                    category = serializer.save(doctor=doctor)
                    created_categories.append(category)
                
                # Return all categories and settings after bulk creation/update
                response_data = {
                    'categories': self.get_serializer(created_categories, many=True).data,
                    'accept_instant_appointment': doctor.accept_instant_appointment,
                    'accept_tamkeen_clinics': doctor.accept_tamkeen_clinics
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            # Single category creation (existing logic)
            existing = PriceCategory.objects.filter(
                doctor=doctor,
                type=request.data.get('type')
            ).first()
            
            if existing:
                return Response(
                    {'detail': 'Price category already exists for this type'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            category = serializer.save(doctor=doctor)
            
            response_data = {
                'categories': [serializer.data],
                'accept_instant_appointment': doctor.accept_instant_appointment,
                'accept_tamkeen_clinics': doctor.accept_tamkeen_clinics
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Doctor.DoesNotExist:
            return Response(
                {'detail': 'Doctor not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except (ValidationError, DRFValidationError) as e:
            return Response(
                {'detail': str(e) if hasattr(e, 'message') else e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=kwargs.get('partial', False)
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except (ValidationError, DRFValidationError) as e:
            return Response(
                {'detail': str(e) if hasattr(e, 'message') else e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
