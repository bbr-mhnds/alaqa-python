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
from .models import Doctor, DoctorVerification
from .serializers import (
    DoctorSerializer, 
    DoctorStatusSerializer,
    DoctorRegistrationSerializer,
    DoctorApprovalSerializer
)
from rest_framework import serializers
from .services import DoctorVerificationService
import logging

logger = logging.getLogger(__name__)

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
            serializer.is_valid(raise_exception=True)
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

    @action(detail=False, methods=['post'], authentication_classes=[], permission_classes=[permissions.AllowAny])
    def initiate(self, request):
        """Step 1: Initiate registration and send verification codes"""
        try:
            # Validate initial data
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            email = serializer.validated_data['email']
            phone = serializer.validated_data['phone']
            
            # Send verification codes
            verification_result = DoctorVerificationService.send_verification_codes(
                email=email,
                phone=phone,
                registration_data=serializer.validated_data
            )
            
            if verification_result['email']['success'] and verification_result['sms']['success']:
                return Response({
                    'status': 'success',
                    'message': 'Verification codes sent successfully',
                    'data': {
                        'verification_id': verification_result.get('verification_id'),
                        'email': verification_result['email']['message'],
                        'sms': verification_result['sms']['message']
                    }
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Failed to send verification codes',
                    'data': {
                        'email': verification_result['email']['message'],
                        'sms': verification_result['sms']['message']
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
                
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
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], authentication_classes=[], permission_classes=[permissions.AllowAny])
    def verify(self, request):
        """Step 2: Verify SMS code"""
        try:
            sms_code = request.data.get('sms_code')
            email = request.data.get('email')  # Add email to find the latest verification
            
            if not all([sms_code, email]):
                return Response({
                    'status': 'error',
                    'message': 'Missing required fields. Please provide sms_code and email.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Find the latest unverified verification for this email
                verification = DoctorVerification.objects.filter(
                    email=email,
                    is_used=False,
                    phone_verified=False
                ).latest('created_at')
            except DoctorVerification.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'No pending verification found for this email'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if verification.is_expired:
                return Response({
                    'status': 'error',
                    'message': 'Verification code has expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify SMS code
            if sms_code == verification.sms_code:
                verification.phone_verified = True
                verification.is_used = True
                verification.save()
                
                # Prepare registration data with file fields
                registration_data = verification.registration_data.copy()
                
                # Transfer files from verification to final paths
                if verification.license_document:
                    registration_data['license_document'] = verification.license_document
                if verification.qualification_document:
                    registration_data['qualification_document'] = verification.qualification_document
                
                # Complete registration
                serializer = self.get_serializer(data=registration_data)
                serializer.is_valid(raise_exception=True)
                doctor = serializer.save()
                
                return Response({
                    'status': 'success',
                    'message': 'Registration successful. Your account is pending approval.',
                    'data': {
                        'doctor': DoctorSerializer(doctor).data,
                        'next_steps': [
                            'Your registration is being reviewed by our team.',
                            'You will receive a notification once your account is approved.',
                            'After approval, you can sign in using your email and password.',
                            'For any questions, please contact our support team.'
                        ]
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Invalid verification code',
                    'data': {
                        'phone_verified': verification.phone_verified
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"[DOCTOR_DEBUG] Registration error: {str(e)}")  # Add logging
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
