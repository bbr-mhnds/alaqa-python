from rest_framework import serializers
from .models import Appointment
from doctors.models import Doctor
from specialties.models import Specialty

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
            'slot_time', 'video_token', 'status', 'created_at'
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