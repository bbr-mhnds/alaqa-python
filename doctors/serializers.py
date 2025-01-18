from rest_framework import serializers
from .models import Doctor
from specialties.serializers import SpecialtySerializer

class DoctorSerializer(serializers.ModelSerializer):
    specialities = SpecialtySerializer(many=True, read_only=True)
    speciality_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    bank_details = serializers.DictField(read_only=True)
    photo = serializers.ImageField(required=False)

    class Meta:
        model = Doctor
        fields = [
            'id', 'name_arabic', 'name', 'sex', 'email', 'phone',
            'experience', 'category', 'language_in_sessions', 'license_number',
            'specialities', 'speciality_ids', 'profile_arabic', 'profile_english',
            'status', 'photo', 'bank_details', 'created_at', 'updated_at',
            'account_holder_name', 'account_number', 'iban_number'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate_phone(self, value):
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with '+'")
        return value

    def validate_email(self, value):
        if Doctor.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return value

    def validate_license_number(self, value):
        if Doctor.objects.filter(license_number=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("A doctor with this license number already exists.")
        return value

    def create(self, validated_data):
        speciality_ids = validated_data.pop('speciality_ids', [])
        doctor = Doctor.objects.create(**validated_data)
        doctor.specialities.set(speciality_ids)
        return doctor

    def update(self, instance, validated_data):
        speciality_ids = validated_data.pop('speciality_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if speciality_ids is not None:
            instance.specialities.set(speciality_ids)
        
        return instance

class DoctorStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'status', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def validate_status(self, value):
        if value not in ['pending', 'approved', 'rejected']:
            raise serializers.ValidationError("Status must be either 'pending', 'approved', or 'rejected'")
        return value 