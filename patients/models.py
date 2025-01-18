from django.db import models
import uuid

class Patient(models.Model):
    class SexChoices(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
    
    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_arabic = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    sex = models.CharField(max_length=10, choices=SexChoices.choices)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )
    photo = models.ImageField(upload_to='patients/photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
