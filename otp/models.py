import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta

class OTP(models.Model):
    """Model for storing OTP codes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=17)
    otp_code = models.CharField(max_length=6)
    attempts = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        indexes = [
            models.Index(fields=['phone_number', 'otp_code']),
            models.Index(fields=['phone_number', 'created_at']),
            models.Index(fields=['otp_code', 'created_at']),
        ]
    
    def __str__(self):
        return f"OTP for {self.phone_number}"
    
    @property
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_verified and not self.is_expired and self.attempts < 3
    
    def save(self, *args, **kwargs):
        # Set expires_at if not set
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)

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
