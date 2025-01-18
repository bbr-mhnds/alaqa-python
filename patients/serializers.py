from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id', 'name_arabic', 'name', 'sex', 'email', 'phone',
            'date_of_birth', 'status', 'photo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Name must be at least 3 characters long')
        return value

    def validate_name_arabic(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Arabic name must be at least 3 characters long')
        return value

    def validate_phone(self, value):
        if not value.strip().isdigit():
            raise serializers.ValidationError('Phone number must contain only digits')
        return value

class PatientStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'status', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def validate_status(self, value):
        if value not in [Patient.StatusChoices.ACTIVE, Patient.StatusChoices.INACTIVE]:
            raise serializers.ValidationError('Invalid status value')
        return value 