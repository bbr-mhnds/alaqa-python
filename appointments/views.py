from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
import requests
from .models import Appointment
from .serializers import AppointmentSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()
    
    def get_permissions(self):
        if self.action in ['create', 'list']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Generate a unique channel name for the video token
        doctor_id = str(serializer.validated_data['doctor'].id)
        slot_time = serializer.validated_data['slot_time'].isoformat()
        
        # Request video token from video calls service
        try:
            response = requests.post(
                'http://localhost:8000/api/v1/video-calls/token/',
                json={
                    'doctor_id': doctor_id,
                    'slot_time': slot_time
                }
            )
            if response.status_code == 200:
                token_data = response.json()
                serializer.validated_data['video_token'] = token_data['token']
                appointment = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Failed to generate video token'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except requests.RequestException as e:
            return Response(
                {'error': 'Failed to generate video token'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_queryset(self):
        queryset = super().get_queryset()
        doctor_id = self.request.query_params.get('doctor_id')
        status_param = self.request.query_params.get('status')
        
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        return queryset

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = 'CANCELLED'
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data) 