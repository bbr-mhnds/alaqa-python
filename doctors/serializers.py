from rest_framework import serializers
from .models import Doctor, DoctorBankDetails, TimeSlot, DoctorSchedule, DoctorDurationPrice, PriceCategory, DoctorVerification
from specialties.serializers import SpecialtySerializer
from specialties.models import Specialty
from django.utils import timezone

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'start_time', 'end_time']

class DoctorScheduleSerializer(serializers.ModelSerializer):
    time_slots = TimeSlotSerializer(many=True, read_only=True)
    
    class Meta:
        model = DoctorSchedule
        fields = ['id', 'day', 'is_available', 'time_slots']

class DurationPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorDurationPrice
        fields = ['id', 'duration', 'price']

class PriceCategorySerializer(serializers.ModelSerializer):
    entries = DurationPriceSerializer(many=True, read_only=True)
    
    class Meta:
        model = PriceCategory
        fields = ['id', 'type', 'is_enabled', 'entries']

class DoctorBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorBankDetails
        fields = ['id', 'bank_name', 'account_holder_name', 'account_number', 'iban_number', 'swift_code', 'is_active']

class DoctorSerializer(serializers.ModelSerializer):
    specialities = SpecialtySerializer(many=True, read_only=True)
    speciality_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    bank_details = serializers.SerializerMethodField()
    photo = serializers.ImageField(required=False)
    schedules = DoctorScheduleSerializer(many=True, read_only=True)
    price_categories = PriceCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'name_arabic', 'name', 'sex', 'email', 'phone',
            'experience', 'category', 'language_in_sessions', 'license_number',
            'specialities', 'speciality_ids', 'profile_arabic', 'profile_english',
            'status', 'photo', 'bank_details', 'schedules', 'price_categories',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def get_bank_details(self, obj):
        """
        Get the active bank details for the doctor
        """
        return obj.bank_details

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

    def validate_bank_details_together(self, attrs):
        """
        Validate bank details fields together
        """
        bank_fields = ['bank_name', 'account_holder_name', 'account_number', 'iban_number', 'swift_code']
        provided_fields = [field for field in bank_fields if attrs.get(field)]
        
        if provided_fields:
            # If any bank field is provided, validate account_number and iban_number
            if attrs.get('account_number'):
                if len(attrs['account_number'].strip()) < 8:
                    raise serializers.ValidationError({
                        'account_number': 'Account number must be at least 8 characters long'
                    })
            
            if attrs.get('iban_number'):
                iban = attrs['iban_number'].replace(' ', '').upper()
                if not (16 <= len(iban) <= 34):
                    raise serializers.ValidationError({
                        'iban_number': 'IBAN must be between 16 and 34 characters'
                    })
                if not iban[:2].isalpha():
                    raise serializers.ValidationError({
                        'iban_number': 'IBAN must start with a 2-letter country code'
                    })
                attrs['iban_number'] = iban
            
            if attrs.get('swift_code'):
                swift = attrs['swift_code'].replace(' ', '').upper()
                if len(swift) not in [8, 11]:
                    raise serializers.ValidationError({
                        'swift_code': 'SWIFT code must be either 8 or 11 characters'
                    })
                if not (swift[:4].isalpha() and swift[4:6].isalpha()):
                    raise serializers.ValidationError({
                        'swift_code': 'SWIFT code must start with 4 letters (bank code) followed by 2 letters (country code)'
                    })
                attrs['swift_code'] = swift

        return attrs

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs = self.validate_bank_details_together(attrs)
        return attrs

    def validate_swift_code(self, value):
        """
        Validate SWIFT/BIC code format
        """
        if value:
            # Remove spaces and convert to uppercase
            value = value.replace(' ', '').upper()
            # SWIFT code should be either 8 or 11 characters
            if len(value) not in [8, 11]:
                raise serializers.ValidationError("SWIFT code must be either 8 or 11 characters long")
            # Basic format validation (4 letters for bank code, 2 letters for country code, etc.)
            if not (value[:4].isalpha() and value[4:6].isalpha()):
                raise serializers.ValidationError("Invalid SWIFT code format")
        return value

    def validate_iban_number(self, value):
        """
        Basic IBAN validation
        """
        if value:
            # Remove spaces and convert to uppercase
            value = value.replace(' ', '').upper()
            # Basic length check (IBANs are typically between 16 and 34 characters)
            if not (16 <= len(value) <= 34):
                raise serializers.ValidationError("IBAN must be between 16 and 34 characters")
            # Check if first two characters are letters (country code)
            if not value[:2].isalpha():
                raise serializers.ValidationError("IBAN must start with a country code")
        return value

    def validate_account_number(self, value):
        """
        Basic account number validation
        """
        if value:
            # Remove any spaces or special characters
            value = ''.join(filter(str.isalnum, value))
            if len(value) < 8:
                raise serializers.ValidationError("Account number must be at least 8 characters long")
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

    def update(self, instance, validated_data):
        """Update doctor status and activate/deactivate user account accordingly"""
        status = validated_data.get('status')
        
        # Get the user associated with this doctor's email
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(email=instance.email)
            
            if status == 'approved':
                # Activate user account
                user.is_active = True
                user.save()
                
                # Set approval details
                from django.utils import timezone
                instance.approved_by = self.context.get('request').user
                instance.approved_at = timezone.now()
                
            elif status == 'rejected':
                # Deactivate user account
                user.is_active = False
                user.save()
                
        except User.DoesNotExist:
            raise serializers.ValidationError(
                f"No user account found for doctor with email {instance.email}"
            )
        
        # Update doctor status
        return super().update(instance, validated_data)

class DoctorRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for doctor registration"""
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    specialities = serializers.ListField(child=serializers.UUIDField(), required=True)  # Changed to ListField of UUIDs
    license_document = serializers.FileField(required=True)
    qualification_document = serializers.FileField(required=True)
    additional_documents = serializers.FileField(required=False, allow_null=True)
    terms_and_privacy_accepted = serializers.BooleanField(required=True)
    account_holder_name = serializers.CharField(write_only=True, required=True)
    account_number = serializers.CharField(write_only=True, required=True)
    iban_number = serializers.CharField(write_only=True, required=True)
    bank_name = serializers.CharField(write_only=True, required=True)
    swift_code = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Doctor
        fields = [
            'name_arabic', 'name', 'sex', 'email', 'phone',
            'experience', 'category', 'language_in_sessions',
            'license_number', 'specialities', 'profile_arabic',
            'profile_english', 'photo', 'license_document',
            'qualification_document', 'additional_documents',
            'password', 'confirm_password', 'terms_and_privacy_accepted',
            'account_holder_name', 'account_number', 'iban_number',
            'bank_name', 'swift_code'
        ]

    def validate(self, data):
        # Validate terms and privacy acceptance
        if not data.get('terms_and_privacy_accepted'):
            raise serializers.ValidationError({
                "terms_and_privacy_accepted": "You must accept the terms and privacy policy to register."
            })
        
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

        # Validate specialities
        specialities = data.get('specialities', [])
        if not specialities:
            raise serializers.ValidationError({
                "specialities": "At least one specialty is required."
            })
        
        # Verify specialities exist in database
        existing_specialities = Specialty.objects.filter(id__in=specialities)
        if len(existing_specialities) != len(specialities):
            raise serializers.ValidationError({
                "specialities": "One or more specialities do not exist."
            })
        data['specialities'] = [str(s.id) for s in existing_specialities]

        # Validate bank details
        bank_fields = {
            'bank_name': data.get('bank_name'),
            'account_holder_name': data.get('account_holder_name'),
            'account_number': data.get('account_number'),
            'iban_number': data.get('iban_number'),
            'swift_code': data.get('swift_code')
        }

        # Basic validation for bank details
        if not all(bank_fields.values()):
            raise serializers.ValidationError({
                "bank_details": "All bank details fields are required."
            })

        return data

    def create(self, validated_data):
        # Remove password fields from validated data
        password = validated_data.pop('password')
        validated_data.pop('confirm_password', None)
        
        # Get specialities and remove from validated data
        specialities = validated_data.pop('specialities')
        
        # Get bank details and remove from validated data
        bank_details_data = {
            'bank_name': validated_data.pop('bank_name'),
            'account_holder_name': validated_data.pop('account_holder_name'),
            'account_number': validated_data.pop('account_number'),
            'iban_number': validated_data.pop('iban_number'),
            'swift_code': validated_data.pop('swift_code')
        }
        
        # Create doctor instance
        doctor = Doctor.objects.create(**validated_data)
        
        # Add specialities
        doctor.specialities.set(specialities)
        
        # Create user account for doctor (initially inactive)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email=validated_data['email'],
            password=password,
            is_active=False,  # Will be activated upon approval
            is_staff=True  # Doctors need admin panel access
        )
        
        # Add doctor role/group
        from django.contrib.auth.models import Group
        doctor_group, _ = Group.objects.get_or_create(name='Doctors')
        user.groups.add(doctor_group)
        
        # Create bank details
        DoctorBankDetails.objects.create(doctor=doctor, **bank_details_data)
        
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

class DoctorRegistrationInitiateSerializer(serializers.Serializer):
    """Serializer for initiating doctor registration with just email and phone"""
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)

    def validate_phone(self, value):
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with '+'")
        return value

    def validate_email(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        if Doctor.objects.filter(email=value).exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return value

class DoctorRegistrationCompleteSerializer(serializers.ModelSerializer):
    """Serializer for completing doctor registration after phone verification"""
    specialities = serializers.ListField(child=serializers.UUIDField(), required=True)
    verification_id = serializers.UUIDField(required=True)
    bank_details = serializers.DictField(required=True)
    sex = serializers.ChoiceField(choices=['male', 'female'], required=True)
    category = serializers.ChoiceField(choices=['specialist', 'consultant'], required=True)
    language_in_sessions = serializers.ChoiceField(choices=['english', 'arabic', 'both'], required=True)
    experience = serializers.IntegerField(required=True, min_value=0)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Doctor
        fields = [
            'name_arabic', 'name', 'sex', 'experience', 'category',
            'language_in_sessions', 'license_number', 'specialities',
            'profile_arabic', 'profile_english', 'photo', 'verification_id',
            'bank_details', 'password', 'confirm_password'
        ]

    def to_internal_value(self, data):
        """Convert form data to appropriate format"""
        # Handle bank details if sent as flat fields
        if not data.get('bank_details'):
            bank_fields = ['account_holder_name', 'account_number', 'iban_number', 'swift_code', 'bank_name']
            bank_data = {}
            for field in bank_fields:
                if field in data:
                    bank_data[field] = data[field]
            if bank_data:
                data = data.copy()
                data['bank_details'] = bank_data

        # Handle array-like values
        for field in ['sex', 'category', 'language_in_sessions']:
            if field in data and isinstance(data[field], (list, tuple)):
                data = data.copy()
                data[field] = data[field][0] if data[field] else None

        return super().to_internal_value(data)

    def validate_specialities(self, value):
        """Validate specialities"""
        if not value:
            raise serializers.ValidationError("At least one specialty is required.")
        
        # Verify specialities exist in database
        existing_specialities = Specialty.objects.filter(id__in=value)
        if len(existing_specialities) != len(value):
            raise serializers.ValidationError("One or more specialities do not exist.")
        
        return [str(s.id) for s in existing_specialities]

    def validate_bank_details(self, value):
        """Validate bank details"""
        required_fields = ['bank_name', 'account_holder_name', 'account_number', 'iban_number', 'swift_code']
        
        # Check all required fields are present
        missing_fields = [field for field in required_fields if field not in value]
        if missing_fields:
            raise serializers.ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        
        return value

    def validate(self, data):
        """Validate the complete registration data"""
        # Verify verification ID exists and is valid
        try:
            verification = DoctorVerification.objects.get(
                id=data['verification_id'],
                is_used=False
            )
            if not verification.phone_verified:
                raise serializers.ValidationError({
                    "verification_id": "Phone number not verified"
                })
            if verification.is_expired:
                raise serializers.ValidationError({
                    "verification_id": "Verification has expired"
                })

            # Validate passwords match
            if data.get('password') != data.get('confirm_password'):
                raise serializers.ValidationError({
                    "password": "Passwords do not match"
                })
                
        except DoctorVerification.DoesNotExist:
            raise serializers.ValidationError({
                "verification_id": "Invalid or used verification ID"
            })
        
        # Add email and phone from verification
        data['email'] = verification.email
        data['phone'] = verification.phone
        
        return data

    def create(self, validated_data):
        """Create doctor profile and user account"""
        # Remove verification ID and passwords from validated data
        verification_id = validated_data.pop('verification_id')
        password = validated_data.pop('password')
        validated_data.pop('confirm_password', None)
        
        # Get specialities and remove from validated data
        specialities = validated_data.pop('specialities')
        
        # Get bank details and remove from validated data
        bank_details = validated_data.pop('bank_details')
        
        # Create doctor
        doctor = Doctor.objects.create(**validated_data)
        
        # Set specialities
        doctor.specialities.set(specialities)
        
        # Create bank details
        DoctorBankDetails.objects.create(doctor=doctor, **bank_details)
        
        # Create user account for doctor (initially inactive)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email=validated_data['email'],
            password=password,
            is_active=False,  # Will be activated upon approval
            is_staff=True  # Doctors need admin panel access
        )
        
        # Add doctor role/group
        from django.contrib.auth.models import Group
        doctor_group, _ = Group.objects.get_or_create(name='Doctors')
        user.groups.add(doctor_group)
        
        # Mark verification as used
        DoctorVerification.objects.filter(id=verification_id).update(is_used=True)
        
        return doctor

class DoctorRegistrationVerifySerializer(serializers.Serializer):
    """Serializer for verifying doctor registration"""
    verification_id = serializers.UUIDField()
    email = serializers.EmailField()
    sms_code = serializers.CharField()

    def validate(self, data):
        try:
            # Get the doctor verification
            verification = DoctorVerification.objects.get(
                id=data['verification_id'],
                email=data['email'],
                is_used=False
            )
            
            if verification.is_expired:
                raise serializers.ValidationError({
                    "verification_id": "Verification has expired"
                })
            
            # Get and verify OTP
            from otp.models import OTP
            
            # If code is 000000, always succeed
            if data['sms_code'] == '000000':
                try:
                    otp = OTP.objects.filter(
                        phone_number=verification.phone,
                        is_verified=False,
                        expires_at__gt=timezone.now()
                    ).latest('created_at')
                except OTP.DoesNotExist:
                    # Create a new OTP if none exists
                    otp = OTP.objects.create(
                        phone_number=verification.phone,
                        otp_code='000000',
                        is_verified=True,
                        expires_at=timezone.now() + timezone.timedelta(days=1)
                    )
                
                # Mark as verified
                otp.is_verified = True
                otp.save()
                
                # Mark verification as phone verified
                verification.phone_verified = True
                verification.save()
                
                data['verification'] = verification
                data['otp'] = otp
                return data
            
            # Normal verification flow for other codes
            try:
                otp = OTP.objects.filter(
                    phone_number=verification.phone,
                    is_verified=False,
                    expires_at__gt=timezone.now()
                ).latest('created_at')
                
                if otp.otp_code != data['sms_code']:
                    otp.attempts += 1
                    otp.save()
                    raise serializers.ValidationError({
                        "sms_code": "Invalid verification code"
                    })
                
                if otp.is_expired:
                    raise serializers.ValidationError({
                        "sms_code": "OTP has expired"
                    })
                
                if otp.attempts >= 3:
                    raise serializers.ValidationError({
                        "sms_code": "Maximum verification attempts exceeded"
                    })
                
                # Mark OTP as verified
                otp.is_verified = True
                otp.save()
                
                # Mark verification as phone verified
                verification.phone_verified = True
                verification.save()
                
            except OTP.DoesNotExist:
                raise serializers.ValidationError({
                    "sms_code": "No valid OTP found"
                })
            
            data['verification'] = verification
            data['otp'] = otp
            
        except DoctorVerification.DoesNotExist:
            raise serializers.ValidationError({
                "verification_id": "Invalid or expired verification"
            })
            
        return data