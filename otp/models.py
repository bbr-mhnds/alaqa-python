import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta

class OTP(models.Model):
    """
    Model to store OTP records with validation and expiry functionality
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['phone_number', 'is_verified']),
        ]

    def __str__(self):
        return f"{self.phone_number} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Set expiry to 10 minutes from creation
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_expired and not self.is_verified and self.attempts < 3

    def get_status_display(self):
        """Get human-readable status"""
        if self.is_verified:
            return "Verified"
        elif self.is_expired:
            return "Expired"
        elif self.attempts >= 3:
            return "Max Attempts"
        return "Active"

    def get_remaining_time(self):
        """Get remaining time before expiry"""
        if self.is_expired:
            return "Expired"
        
        remaining = self.expires_at - timezone.now()
        minutes = remaining.seconds // 60
        seconds = remaining.seconds % 60
        return f"{minutes}m {seconds}s"

    def get_attempts_display(self):
        """Get human-readable attempts status"""
        return f"{self.attempts}/3 attempts"
