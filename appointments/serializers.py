from rest_framework import serializers
from .models import Appointment
from doctors.models import Doctor
from specialties.models import Specialty
from django.utils import timezone
import time
import random
from video_calls.views import generate_agora_rtc_token

class AppointmentCompletionSerializer(serializers.Serializer):
    completion_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    duration_minutes = serializers.IntegerField(required=False, allow_null=True)
    completion_time = serializers.DateTimeField(required=False, allow_null=True)

    def validate_duration_minutes(self, value):
        """
        Validate that duration_minutes is greater than 0 if provided.
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError("Duration minutes must be greater than 0")
        return value

    def validate(self, data):
        """
        Additional validation for completion data.
        At least one field should be provided with a valid value.
        Empty strings and None values are allowed.
        """
        # Check if any field is provided in the request
        if not data:
            raise serializers.ValidationError({
                "non_field_errors": ["At least one field must be provided"]
            })
            
        return data

class AppointmentSerializer(serializers.ModelSerializer):
    specialties = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Specialty.objects.all()
    )
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all()
    )

    class Meta:
        model = Appointment
        fields = [
            'id', 'doctor', 'specialties', 'specialist_category',
            'gender', 'duration', 'language', 'phone_number',
            'slot_time', 'video_token', 'status', 'created_at',
            'completion_notes', 'completion_time',
            'duration_minutes', 'patient_id', 'updated_at'
        ]
        read_only_fields = ['video_token', 'status', 'created_at']

    def validate_phone_number(self, value):
        # Remove any non-digit characters
        cleaned_number = ''.join(filter(str.isdigit, value))
        if len(cleaned_number) < 9:
            raise serializers.ValidationError("Phone number must have at least 9 digits")
        return cleaned_number

    def validate(self, data):
        # Check if the doctor is associated with any of the selected specialties
        doctor = data['doctor']
        specialties = data['specialties']
        
        # Get all specialties for the doctor
        doctor_specialties = set(doctor.specialities.all())
        
        # Check if there's any overlap between selected specialties and doctor's specialties
        if not any(specialty in doctor_specialties for specialty in specialties):
            raise serializers.ValidationError(
                "Selected doctor must be associated with at least one of the selected specialties"
            )
        
        return data

    def create(self, validated_data):
        try:
            # Generate a unique channel name based on doctor_id and slot_time
            slot_time = validated_data['slot_time']
            doctor_id = validated_data['doctor'].id
            cleaned_slot_time = slot_time.strftime('%Y%m%d%H%M%S')
            channel_name = f"vid_{doctor_id}_{cleaned_slot_time}"

            # Generate a unique uid for the video call
            timestamp_part = int(str(int(time.time()))[-4:])  # Last 4 digits of timestamp
            random_part = random.randint(1, 999)
            uid = int(f"{timestamp_part}{random_part}")  # Combine for unique ID

            # Generate the video token
            token, _ = generate_agora_rtc_token(channel_name, uid)

            # Add the video token to the validated data
            validated_data['video_token'] = token

            # Create the appointment
            appointment = super().create(validated_data)
            return appointment

        except Exception as e:
            raise serializers.ValidationError(f"Failed to create appointment: {str(e)}") 