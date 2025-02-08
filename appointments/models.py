from django.db import models
from django.core.validators import MinLengthValidator
from doctors.models import Doctor
from specialties.models import Specialty

class Appointment(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show')
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    specialties = models.ManyToManyField(Specialty, related_name='appointments')
    specialist_category = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    duration = models.CharField(max_length=20)  # Store duration in minutes
    language = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, validators=[MinLengthValidator(9)])
    slot_time = models.DateTimeField()
    video_token = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    # Completion fields
    completion_notes = models.TextField(blank=True, null=True)
    completion_time = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    patient_id = models.CharField(max_length=100, blank=True, null=True)  # Made nullable for existing records
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-slot_time']

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.name} at {self.slot_time}" 