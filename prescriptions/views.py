from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from appointments.models import Appointment
from doctors.models import Doctor
from patients.models import Patient
from .models import Prescription, PrescribedDrug, TestRecommendation
from .serializers import (
    PrescriptionSerializer,
    PrescriptionCreateSerializer,
    PrescribedDrugSerializer,
    TestRecommendationSerializer
)

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PrescriptionCreateSerializer
        return PrescriptionSerializer

    def get_queryset(self):
        user = self.request.user
        
        # Filter based on user role
        try:
            doctor = Doctor.objects.get(email=user.email)
            return Prescription.objects.filter(appointment__doctor=doctor)
        except Doctor.DoesNotExist:
            try:
                patient = Patient.objects.get(email=user.email)
                return Prescription.objects.filter(appointment__patient=patient)
            except Patient.DoesNotExist:
                return Prescription.objects.none()

    def check_appointment_permission(self, appointment):
        """Check if user has permission to access/modify the appointment"""
        user = self.request.user
        
        try:
            doctor = Doctor.objects.get(email=user.email)
            if appointment.doctor == doctor:
                return 'doctor'
        except Doctor.DoesNotExist:
            try:
                patient = Patient.objects.get(email=user.email)
                if appointment.patient == patient:
                    return 'patient'
            except Patient.DoesNotExist:
                pass
        
        raise PermissionDenied("You don't have permission to access this appointment")

    def perform_create(self, serializer):
        appointment = get_object_or_404(
            Appointment,
            id=self.request.data.get('appointment')
        )
        
        # Only doctors can create prescriptions
        role = self.check_appointment_permission(appointment)
        if role != 'doctor':
            raise PermissionDenied("Only doctors can create prescriptions")
        
        # Check if prescription already exists
        if Prescription.objects.filter(appointment=appointment).exists():
            raise PermissionDenied("Prescription already exists for this appointment")
        
        serializer.save()

    def perform_update(self, serializer):
        # Only doctors can update prescriptions
        appointment = serializer.instance.appointment
        role = self.check_appointment_permission(appointment)
        if role != 'doctor':
            raise PermissionDenied("Only doctors can update prescriptions")
        
        serializer.save()

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Generate and download prescription as PDF"""
        prescription = self.get_object()
        
        # TODO: Implement PDF generation
        # For now, return a message
        return Response({
            "message": "PDF download will be implemented soon"
        })

class PrescribedDrugViewSet(viewsets.ModelViewSet):
    serializer_class = PrescribedDrugSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PrescribedDrug.objects.filter(
            prescription_id=self.kwargs['prescription_pk']
        )
    
    def perform_create(self, serializer):
        prescription = get_object_or_404(
            Prescription,
            id=self.kwargs['prescription_pk']
        )
        # Check if user is the doctor for this prescription
        if not Doctor.objects.filter(
            email=self.request.user.email,
            appointments__prescription=prescription
        ).exists():
            raise PermissionDenied("Only the prescribing doctor can add drugs")
        
        serializer.save(prescription=prescription)

class TestRecommendationViewSet(viewsets.ModelViewSet):
    serializer_class = TestRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TestRecommendation.objects.filter(
            prescription_id=self.kwargs['prescription_pk']
        )
    
    def perform_create(self, serializer):
        prescription = get_object_or_404(
            Prescription,
            id=self.kwargs['prescription_pk']
        )
        # Check if user is the doctor for this prescription
        if not Doctor.objects.filter(
            email=self.request.user.email,
            appointments__prescription=prescription
        ).exists():
            raise PermissionDenied("Only the prescribing doctor can add test recommendations")
        
        serializer.save(prescription=prescription) 