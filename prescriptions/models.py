from django.db import models
from django.core.validators import MinValueValidator
from appointments.models import Appointment
from drugs.models import Drug

class Prescription(models.Model):
    """Main prescription model linked to an appointment"""
    appointment = models.OneToOneField(
        Appointment, 
        on_delete=models.CASCADE,
        related_name='prescription'
    )
    diagnosis = models.TextField(help_text="Doctor's diagnosis")
    notes = models.TextField(blank=True, help_text="Additional notes from doctor")
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prescription for {self.appointment}"

    class Meta:
        ordering = ['-created_at']

class PrescribedDrug(models.Model):
    """Individual drug prescriptions within a prescription"""
    FREQUENCY_CHOICES = [
        ('OD', 'Once daily'),
        ('BD', 'Twice daily'),
        ('TDS', 'Three times a day'),
        ('QDS', 'Four times a day'),
        ('PRN', 'As needed'),
        ('STAT', 'Immediately'),
        ('OTHER', 'Other (see notes)')
    ]

    DURATION_UNIT_CHOICES = [
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months')
    ]

    ROUTE_CHOICES = [
        ('oral', 'Oral'),
        ('topical', 'Topical'),
        ('injection', 'Injection'),
        ('inhaler', 'Inhaler'),
        ('drops', 'Drops'),
        ('other', 'Other')
    ]

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='prescribed_drugs'
    )
    drug = models.ForeignKey(
        Drug,
        on_delete=models.PROTECT,  # Don't delete drug records if referenced
        related_name='prescriptions'
    )
    dosage = models.CharField(
        max_length=100,
        help_text="Dosage per intake (e.g., '500mg', '2 tablets')"
    )
    frequency = models.CharField(
        max_length=10,
        choices=FREQUENCY_CHOICES,
        help_text="How often to take the medication"
    )
    duration = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Duration of the prescription"
    )
    duration_unit = models.CharField(
        max_length=10,
        choices=DURATION_UNIT_CHOICES,
        default='days'
    )
    route = models.CharField(
        max_length=10,
        choices=ROUTE_CHOICES,
        default='oral'
    )
    instructions = models.TextField(
        blank=True,
        help_text="Special instructions for taking this medication"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.drug.name} - {self.dosage} {self.frequency}"

    class Meta:
        ordering = ['drug__name']

class TestRecommendation(models.Model):
    """Medical tests recommended by the doctor"""
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='test_recommendations'
    )
    test_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    urgency = models.CharField(
        max_length=20,
        choices=[
            ('routine', 'Routine'),
            ('urgent', 'Urgent'),
            ('emergency', 'Emergency')
        ],
        default='routine'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.test_name} for {self.prescription.appointment}"

    class Meta:
        ordering = ['urgency', 'test_name'] 