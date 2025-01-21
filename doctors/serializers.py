from rest_framework import serializers
from .models import Doctor
from specialties.serializers import SpecialtySerializer
from specialties.models import Specialty

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

class DoctorRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for doctor registration"""
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    specialities = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Specialty.objects.all(),
        required=True
    )

    class Meta:
        model = Doctor
        fields = [
            'name_arabic', 'name', 'sex', 'email', 'phone',
            'experience', 'category', 'language_in_sessions',
            'license_number', 'specialities', 'profile_arabic',
            'profile_english', 'photo', 'license_document',
            'qualification_document', 'additional_documents',
            'password', 'confirm_password'
        ]
        extra_kwargs = {
            'license_document': {'required': True},
            'qualification_document': {'required': True}
        }

    def validate(self, data):
        # Validate passwords match
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        
        # Validate email uniqueness
        email = data.get('email')
        if email:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({
                    "email": "A user with this email already exists."
                })
        return data

    def create(self, validated_data):
        # Remove password fields from validated data
        password = validated_data.pop('password')
        validated_data.pop('confirm_password', None)
        
        # Create doctor instance
        specialities = validated_data.pop('specialities')
        doctor = Doctor.objects.create(**validated_data)
        
        # Add specialities
        doctor.specialities.set(specialities)
        
        # Create user account for doctor (initially inactive)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=password,
            is_active=False,  # Will be activated upon approval
            is_staff=True  # Doctors need admin panel access
        )
        
        # Add doctor role/group
        from django.contrib.auth.models import Group
        doctor_group, _ = Group.objects.get_or_create(name='Doctors')
        user.groups.add(doctor_group)
        
        return doctor

class DoctorApprovalSerializer(serializers.ModelSerializer):
    """Serializer for doctor approval/rejection"""
    class Meta:
        model = Doctor
        fields = ['status', 'rejection_reason']
        extra_kwargs = {
            'rejection_reason': {'required': False}
        }

    def validate(self, data):
        if data.get('status') == 'rejected' and not data.get('rejection_reason'):
            raise serializers.ValidationError(
                "Rejection reason is required when rejecting a doctor"
            )
        return data

    def update(self, instance, validated_data):
        request = self.context.get('request')
        status = validated_data.get('status')
        
        if status == 'approved':
            # Set approval details
            from django.utils import timezone
            instance.approved_by = request.user
            instance.approved_at = timezone.now()
            
            # Activate the user account
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(email=instance.email)
                user.is_active = True
                user.save()
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "User account not found for this doctor"
                )
        
        return super().update(instance, validated_data) 