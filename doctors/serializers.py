from rest_framework import serializers
from .models import Doctor, DoctorBankDetails, TimeSlot, DoctorSchedule, DoctorDurationPrice, PriceCategory, DoctorVerification
from specialties.serializers import SpecialtySerializer
from specialties.models import Specialty

class DoctorSerializer(serializers.ModelSerializer):
    specialities = SpecialtySerializer(many=True, read_only=True)
    speciality_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    bank_details = serializers.SerializerMethodField()
    photo = serializers.ImageField(required=False)

    class Meta:
        model = Doctor
        fields = [
            'id', 'name_arabic', 'name', 'sex', 'email', 'phone',
            'experience', 'category', 'language_in_sessions', 'license_number',
            'specialities', 'speciality_ids', 'profile_arabic', 'profile_english',
            'status', 'photo', 'bank_details', 'created_at', 'updated_at'
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

class DoctorRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for doctor registration"""
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    specialities = serializers.JSONField(required=True)  # Changed to JSONField
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

        # Validate and convert specialities
        specialities = data.get('specialities', [])
        if not isinstance(specialities, list):
            try:
                import json
                specialities = json.loads(specialities)
            except (json.JSONDecodeError, TypeError):
                raise serializers.ValidationError({
                    "specialities": "Invalid format. Expected a JSON array of UUIDs."
                })
        
        try:
            import uuid
            # Convert string UUIDs to UUID objects
            uuid_list = [uuid.UUID(str(s)) for s in specialities]
            existing_specialities = Specialty.objects.filter(id__in=uuid_list)
            if len(existing_specialities) != len(specialities):
                raise serializers.ValidationError({
                    "specialities": "One or more specialities do not exist."
                })
            data['specialities'] = [str(s.id) for s in existing_specialities]  # Convert UUIDs to strings
        except ValueError:
            raise serializers.ValidationError({
                "specialities": "Invalid UUID format for specialities."
            })

        # Validate bank details
        bank_details = DoctorBankDetails(
            bank_name=data.get('bank_name'),
            account_holder_name=data.get('account_holder_name'),
            account_number=data.get('account_number'),
            iban_number=data.get('iban_number'),
            swift_code=data.get('swift_code')
        )
        try:
            bank_details.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

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

class DoctorBankDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for DoctorBankDetails model
    """
    class Meta:
        model = DoctorBankDetails
        fields = [
            'id', 'doctor', 'bank_name', 'account_holder_name',
            'account_number', 'iban_number', 'swift_code',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'doctor': {'write_only': True}
        }

    def validate(self, attrs):
        # Clean the data using model's clean method
        instance = DoctorBankDetails(**attrs)
        instance.clean()
        return attrs

class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for TimeSlot model"""
    class Meta:
        model = TimeSlot
        fields = ['id', 'start_time', 'end_time']
        read_only_fields = ['id']

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if start_time and end_time:
            # Validate time format
            time_format = "%H:%M"
            try:
                start_str = start_time.strftime(time_format)
                end_str = end_time.strftime(time_format)
            except ValueError:
                raise serializers.ValidationError({
                    'time_slots': ['Time must be in 24-hour format (HH:mm)']
                })

            # Validate end time is after start time
            if end_time <= start_time:
                raise serializers.ValidationError({
                    'time_slots': ['End time must be after start time']
                })

        return attrs

class DoctorScheduleSerializer(serializers.ModelSerializer):
    """Serializer for DoctorSchedule model"""
    time_slots = TimeSlotSerializer(many=True, required=False)

    class Meta:
        model = DoctorSchedule
        fields = ['day', 'is_available', 'time_slots']

    def validate(self, attrs):
        is_available = attrs.get('is_available', True)
        time_slots_data = attrs.get('time_slots', [])

        if is_available and not time_slots_data and self.context.get('check_slots', True):
            raise serializers.ValidationError({
                'time_slots': ['Time slots are required when the day is available']
            })

        # Validate time slots don't overlap
        if time_slots_data:
            slots = sorted(time_slots_data, key=lambda x: x['start_time'])
            for i in range(1, len(slots)):
                if slots[i]['start_time'] <= slots[i-1]['end_time']:
                    raise serializers.ValidationError({
                        'time_slots': ['Time slots cannot overlap']
                    })

        return attrs

    def create(self, validated_data):
        time_slots_data = validated_data.pop('time_slots', [])
        schedule = DoctorSchedule.objects.create(**validated_data)

        for slot_data in time_slots_data:
            TimeSlot.objects.create(schedule=schedule, **slot_data)

        return schedule

    def update(self, instance, validated_data):
        time_slots_data = validated_data.pop('time_slots', [])
        
        # Update schedule fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # If is_available is False, delete all time slots
        if not instance.is_available:
            instance.time_slots.all().delete()
        else:
            # Update time slots
            instance.time_slots.all().delete()  # Remove existing slots
            for slot_data in time_slots_data:
                TimeSlot.objects.create(schedule=instance, **slot_data)

        return instance

class DurationPriceSerializer(serializers.ModelSerializer):
    """Serializer for duration-based price entries"""
    class Meta:
        model = DoctorDurationPrice
        fields = ['duration', 'price']

    def validate_duration(self, value):
        if value < 5:
            raise serializers.ValidationError("Duration must be at least 5 minutes")
        if value % 5 != 0:
            raise serializers.ValidationError("Duration must be in increments of 5 minutes")
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value

class PriceCategorySerializer(serializers.ModelSerializer):
    """Serializer for price categories with nested duration prices"""
    entries = DurationPriceSerializer(many=True, required=False)

    class Meta:
        model = PriceCategory
        fields = ['type', 'is_enabled', 'entries']

    def validate(self, attrs):
        is_enabled = attrs.get('is_enabled', True)
        entries = attrs.get('entries', [])

        if is_enabled and not entries and self.context.get('check_entries', True):
            raise serializers.ValidationError({
                'entries': 'At least one duration-price entry is required when category is enabled'
            })

        # Check for duplicate durations
        if entries:
            durations = [entry['duration'] for entry in entries]
            if len(durations) != len(set(durations)):
                raise serializers.ValidationError({
                    'entries': 'Duplicate durations are not allowed'
                })

            # Check maximum entries
            if len(entries) > 10:
                raise serializers.ValidationError({
                    'entries': 'Maximum 10 entries allowed per category'
                })

        return attrs

    def create(self, validated_data):
        entries_data = validated_data.pop('entries', [])
        category = PriceCategory.objects.create(**validated_data)

        for entry_data in entries_data:
            DoctorDurationPrice.objects.create(category=category, **entry_data)

        return category

    def update(self, instance, validated_data):
        entries_data = validated_data.pop('entries', [])
        
        # Update category fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # If category is disabled, remove all entries
        if not instance.is_enabled:
            instance.entries.all().delete()
        else:
            # Update entries
            instance.entries.all().delete()  # Remove existing entries
            for entry_data in entries_data:
                DoctorDurationPrice.objects.create(category=instance, **entry_data)

        return instance

class DoctorRegistrationInitiateSerializer(serializers.Serializer):
    """Serializer for initiating doctor registration"""
    email = serializers.EmailField()
    phone = serializers.CharField()

    def validate_email(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone(self, value):
        # Remove any non-digit characters
        cleaned_number = ''.join(filter(str.isdigit, value))
        if len(cleaned_number) < 9:
            raise serializers.ValidationError("Phone number must have at least 9 digits")
        return cleaned_number

class DoctorRegistrationVerifySerializer(serializers.Serializer):
    """Serializer for verifying doctor registration"""
    verification_id = serializers.IntegerField()
    email = serializers.EmailField()
    sms_code = serializers.CharField()

    def validate(self, data):
        try:
            verification = DoctorVerification.objects.get(
                id=data['verification_id'],
                email=data['email'],
                is_used=False,
                phone_verified=False
            )
            if verification.is_expired:
                raise serializers.ValidationError({
                    "verification_id": "Verification code has expired"
                })
            data['verification'] = verification
        except DoctorVerification.DoesNotExist:
            raise serializers.ValidationError({
                "verification_id": "Invalid or expired verification"
            })
        return data 