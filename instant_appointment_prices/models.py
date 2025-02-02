import uuid
from django.db import models
from django.core.validators import MinValueValidator

class InstantAppointmentPrice(models.Model):
    """
    Model for storing instant appointment prices with duration
    """
    SITE_TYPE_CHOICES = [
        ('clinic', 'Clinic'),
        ('video', 'Video'),
        ('home', 'Home'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duration = models.PositiveIntegerField(
        help_text='Duration in minutes',
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text='Price in currency'
    )
    site_type = models.CharField(
        max_length=50,
        help_text='Type of site for the appointment',
        null=False,
        blank=False,
        default='clinic',
        choices=SITE_TYPE_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['duration']
        verbose_name = 'Instant Appointment Price'
        verbose_name_plural = 'Instant Appointment Prices'
        unique_together = ['duration', 'site_type']

    def __str__(self):
        return f"{self.duration} minutes - {self.price} ({self.site_type})"
