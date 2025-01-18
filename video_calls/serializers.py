from rest_framework import serializers
from django.utils import timezone
from .models import VideoCall
from doctors.serializers import DoctorSerializer
from patients.serializers import PatientSerializer

class VideoCallSerializer(serializers.ModelSerializer):
    doctor_details = DoctorSerializer(source='doctor', read_only=True)
    patient_details = PatientSerializer(source='patient', read_only=True)
    duration = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = VideoCall
        fields = [
            'id', 'channel_name', 'doctor', 'patient', 
            'doctor_details', 'patient_details',
            'status', 'scheduled_time', 'started_at', 
            'ended_at', 'created_at', 'updated_at',
            'duration', 'can_join', 'is_expired'
        ]
        read_only_fields = [
            'channel_name', 'started_at', 'ended_at', 
            'created_at', 'updated_at', 'duration',
            'can_join', 'is_expired'
        ]

    def get_duration(self, obj):
        """Get the duration of the call in minutes"""
        return obj.get_duration()

    def get_can_join(self, obj):
        """Check if the call can be joined"""
        can_join, _ = obj.can_join()
        return can_join

    def get_is_expired(self, obj):
        """Check if the call has expired"""
        return obj.is_expired()

    def validate_scheduled_time(self, value):
        """
        Check that the scheduled time is not in the past and not too far in the future
        """
        now = timezone.now()
        
        if value <= now:
            raise serializers.ValidationError("Scheduled time must be in the future")
            
        # Don't allow scheduling more than 3 months in advance
        max_future = now + timezone.timedelta(days=90)
        if value > max_future:
            raise serializers.ValidationError("Cannot schedule calls more than 3 months in advance")
            
        return value

    def validate(self, data):
        """
        Check that the doctor and patient are valid and available
        """
        if data.get('doctor') and data.get('patient'):
            # Check if doctor and patient are the same person
            if data['doctor'].email == data['patient'].email:
                raise serializers.ValidationError("Doctor and patient cannot be the same person")
            
            # Check if doctor is approved
            if data['doctor'].status != 'approved':
                raise serializers.ValidationError("Doctor is not approved for consultations")
                
            # Check if patient is active
            if data['patient'].status != 'active':
                raise serializers.ValidationError("Patient account is not active")
            
            # Check if there's an overlapping call for either doctor or patient
            overlapping_calls = VideoCall.objects.filter(
                doctor=data['doctor'],
                scheduled_time__lte=data['scheduled_time'] + timezone.timedelta(minutes=30),
                scheduled_time__gte=data['scheduled_time'] - timezone.timedelta(minutes=30),
                status__in=['scheduled', 'ongoing']
            ).exists() or VideoCall.objects.filter(
                patient=data['patient'],
                scheduled_time__lte=data['scheduled_time'] + timezone.timedelta(minutes=30),
                scheduled_time__gte=data['scheduled_time'] - timezone.timedelta(minutes=30),
                status__in=['scheduled', 'ongoing']
            ).exists()

            if overlapping_calls:
                raise serializers.ValidationError(
                    "There is already a scheduled call within 30 minutes of this time"
                )

        return data

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    channel = serializers.CharField()
    uid = serializers.IntegerField()
    app_id = serializers.CharField()
    expiration_time = serializers.DateTimeField()

class TokenRequestSerializer(serializers.Serializer):
    channel_name = serializers.CharField(required=True)
    role = serializers.IntegerField(required=False, default=1)  # 1=publisher, 2=subscriber

    def validate_channel_name(self, value):
        """Validate the channel name"""
        if len(value) < 3:
            raise serializers.ValidationError("Channel name must be at least 3 characters long")
        return value

    def validate_role(self, value):
        """Validate the role"""
        if value not in [1, 2]:  # 1=publisher, 2=subscriber
            raise serializers.ValidationError("Role must be either 1 (publisher) or 2 (subscriber)")
        return value 