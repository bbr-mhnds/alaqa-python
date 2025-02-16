from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.db import models
from .models import Patient
from .serializers import PatientSerializer, PatientStatusSerializer
from services.email_service import EmailService
from otp.services import OTPService
import logging

logger = logging.getLogger(__name__)

class PatientFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Patient.StatusChoices.choices)
    search = filters.CharFilter(method='search_filter')

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(name_arabic__icontains=value) |
            models.Q(email__icontains=value)
        )

    class Meta:
        model = Patient
        fields = ['status', 'search']

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filterset_class = PatientFilter
    search_fields = ['name', 'name_arabic', 'email']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "status": "success",
                "data": {
                    "patients": serializer.data,
                    "pagination": {
                        "total": self.paginator.page.paginator.count,
                        "pages": self.paginator.page.paginator.num_pages,
                        "page": self.paginator.page.number,
                        "limit": self.paginator.page_size
                    }
                }
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "data": {
                "patients": serializer.data
            }
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "status": "success",
            "data": {
                "patient": serializer.data
            }
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "status": "success",
                "data": {
                    "patient": serializer.data
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Invalid request parameters",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "status": "success",
                "data": {
                    "patient": serializer.data
                }
            })
        return Response({
            "status": "error",
            "message": "Invalid request parameters",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": "success",
            "message": "Patient deleted successfully"
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], serializer_class=PatientStatusSerializer)
    def status(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "data": {
                    "patient": serializer.data
                }
            })
        
        return Response({
            "status": "error",
            "message": "Invalid request parameters",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='security-code', permission_classes=[permissions.AllowAny])
    def security_code(self, request, pk=None):
        """Generate and send a security code to patient's email and phone"""
        try:
            patient = self.get_object()
            
            # Initialize services
            otp_service = OTPService()
            email_service = EmailService()
            
            # Generate and send OTP
            otp_result = otp_service.create_and_send_otp(patient.phone)
            
            if not otp_result['success']:
                return Response({
                    'status': 'error',
                    'message': f"Failed to send SMS: {otp_result['message']}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Get the OTP code from the service
            otp = otp_service.get_otp_by_id(otp_result['otp_id'])
            if not otp:
                return Response({
                    'status': 'error',
                    'message': 'Failed to retrieve security code'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Send email with the same code
            email_result = email_service.send_otp_email(patient.email, otp.otp_code)
            
            if not email_result['success']:
                logger.error(f"Failed to send email to {patient.email}: {email_result['message']}")
            
            return Response({
                'status': 'success',
                'message': 'Security code sent successfully',
                'data': {
                    'otp_id': str(otp.id)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception(f"Error sending security code to patient {pk}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
