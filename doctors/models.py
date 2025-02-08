import uuid
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from specialties.models import Specialty
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator

class Doctor(models.Model):
    SEX_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    CATEGORY_CHOICES = (
        ('consultant', 'Consultant'),
        ('specialist', 'Specialist'),
        ('general', 'General Practitioner'),
    )

    LANGUAGE_CHOICES = (
        ('arabic', 'Arabic'),
        ('english', 'English'),
        ('both', 'Both'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_arabic = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17)
    experience = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    language_in_sessions = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    license_number = models.CharField(max_length=100, unique=True)
    specialities = models.ManyToManyField(Specialty, related_name='doctors')
    profile_arabic = models.TextField()
    profile_english = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    photo = models.ImageField(upload_to='doctors/', null=True, blank=True)
    terms_and_privacy_accepted = models.BooleanField(default=False)

    # Approval Management
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_doctors'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    license_document = models.FileField(
        upload_to='doctors/licenses/',
        null=True,
        blank=True,
        help_text='Upload your medical license document'
    )
    qualification_document = models.FileField(
        upload_to='doctors/qualifications/',
        null=True,
        blank=True,
        help_text='Upload your qualification certificates'
    )
    additional_documents = models.FileField(
        upload_to='doctors/additional/',
        null=True,
        blank=True,
        help_text='Any additional supporting documents'
    )

    # Appointment Settings
    accept_instant_appointment = models.BooleanField(default=False)
    accept_tamkeen_clinics = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'

    def __str__(self):
        return f"{self.name} - {self.license_number}"

    @property
    def bank_details(self):
        """
        Get the active bank details for the doctor
        """
        try:
            bank_detail = self.bank_detail
            if bank_detail and bank_detail.is_active:
                return {
                    'bank_name': bank_detail.bank_name,
                    'account_holder_name': bank_detail.account_holder_name,
                    'account_number': bank_detail.account_number,
                    'iban_number': bank_detail.iban_number,
                    'swift_code': bank_detail.swift_code
                }
        except DoctorBankDetails.DoesNotExist:
            pass
        return None

class DoctorVerification(models.Model):
    """Model to store doctor verification data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    phone = models.CharField(max_length=17)
    email_code = models.CharField(max_length=6, default='000000')
    email_verified = models.BooleanField(default=True)  # Always true since we don't use email verification
    phone_verified = models.BooleanField(default=False)
    registration_data = models.JSONField(default=dict)  # Store registration data temporarily
    license_document = models.FileField(upload_to='temp/license_documents/', null=True)
    qualification_document = models.FileField(upload_to='temp/qualification_documents/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Verification for {self.email}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def is_complete(self):
        return self.phone_verified  # Only check phone verification since email is always true

class DoctorBankDetails(models.Model):
    """
    Model for storing doctor bank details separately
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.OneToOneField(
        'Doctor',
        on_delete=models.CASCADE,
        related_name='bank_detail'
    )
    bank_name = models.CharField(max_length=255)
    account_holder_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    iban_number = models.CharField(max_length=50)
    swift_code = models.CharField(max_length=11)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Doctor Bank Detail'
        verbose_name_plural = 'Doctor Bank Details'
        ordering = ['-created_at']

    def __str__(self):
        return f"Bank details for {self.doctor.name}"

    def clean(self):
        # Validate SWIFT code
        if self.swift_code:
            swift = self.swift_code.replace(' ', '').upper()
            if len(swift) not in [8, 11]:
                raise ValidationError({'swift_code': 'SWIFT code must be either 8 or 11 characters'})
            if not (swift[:4].isalpha() and swift[4:6].isalpha()):
                raise ValidationError({
                    'swift_code': 'SWIFT code must start with 4 letters (bank code) followed by 2 letters (country code)'
                })
            self.swift_code = swift

        # Validate IBAN
        if self.iban_number:
            iban = self.iban_number.replace(' ', '').upper()
            if not (16 <= len(iban) <= 34):
                raise ValidationError({'iban_number': 'IBAN must be between 16 and 34 characters'})
            if not iban[:2].isalpha():
                raise ValidationError({'iban_number': 'IBAN must start with a country code'})
            self.iban_number = iban

        # Validate account number
        if self.account_number:
            account_number = ''.join(filter(str.isalnum, self.account_number))
            if len(account_number) < 8:
                raise ValidationError({'account_number': 'Account number must be at least 8 characters long'})
            self.account_number = account_number

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class DoctorSchedule(models.Model):
    """Model for doctor's working schedule"""
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    doctor = models.ForeignKey(
        'Doctor',
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Doctor Schedule'
        verbose_name_plural = 'Doctor Schedules'
        ordering = ['day']
        unique_together = ['doctor', 'day']

    def __str__(self):
        return f"{self.doctor.name}'s schedule for {self.day}"

class TimeSlot(models.Model):
    """Model for time slots within a schedule"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey(
        DoctorSchedule,
        on_delete=models.CASCADE,
        related_name='time_slots'
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'
        ordering = ['start_time']

    def __str__(self):
        return f"{self.schedule.doctor.name} - {self.schedule.day}: {self.start_time} to {self.end_time}"

    def clean(self):
        if self.start_time and self.end_time:
            # Ensure end time is after start time
            if self.end_time <= self.start_time:
                raise ValidationError({
                    'end_time': 'End time must be after start time'
                })

            # Check for overlapping slots
            overlapping = TimeSlot.objects.filter(
                schedule=self.schedule,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            )
            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)
            if overlapping.exists():
                raise ValidationError({
                    'time_slots': 'Time slots cannot overlap'
                })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class PriceCategory(models.Model):
    """Model for price categories (initial consultation, follow up, etc.)"""
    CATEGORY_TYPES = [
        ('initial_consultation', 'Initial Consultation'),
        ('follow_up', 'Follow Up'),
        ('emergency', 'Emergency'),
        ('specialist', 'Specialist'),
    ]

    doctor = models.ForeignKey(
        'Doctor',
        on_delete=models.CASCADE,
        related_name='price_categories'
    )
    type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Price Category'
        verbose_name_plural = 'Price Categories'
        ordering = ['type']
        unique_together = ['doctor', 'type']

    def __str__(self):
        return f"{self.doctor.name} - {self.get_type_display()}"

class DoctorDurationPrice(models.Model):
    """Model for doctor's duration-based pricing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        PriceCategory,
        on_delete=models.CASCADE,
        related_name='entries'
    )
    duration = models.PositiveIntegerField(help_text='Duration in minutes')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Price in USD'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Duration Price'
        verbose_name_plural = 'Duration Prices'
        ordering = ['duration']
        unique_together = ['category', 'duration']

    def __str__(self):
        return f"{self.category.doctor.name} - {self.category.get_type_display()} - {self.duration}min"

    def clean(self):
        if self.duration < 5:
            raise ValidationError({
                'duration': 'Duration must be at least 5 minutes'
            })
        
        if self.duration % 5 != 0:
            raise ValidationError({
                'duration': 'Duration must be in increments of 5 minutes'
            })

        if self.price < 0:
            raise ValidationError({
                'price': 'Price cannot be negative'
            })

        # Check if there are too many entries for this category
        if not self.pk:  # Only check on creation
            existing_count = DoctorDurationPrice.objects.filter(
                category=self.category
            ).count()
            if existing_count >= 10:
                raise ValidationError({
                    'category': 'Maximum 10 entries allowed per category'
                })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
