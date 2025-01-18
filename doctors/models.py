import uuid
from django.db import models
from django.core.validators import RegexValidator
from specialties.models import Specialty

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
    
    # Bank Details
    account_holder_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    iban_number = models.CharField(max_length=50)

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
        return {
            'accountHolderName': self.account_holder_name,
            'accountNumber': self.account_number,
            'ibanNumber': self.iban_number,
        }
