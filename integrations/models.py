from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Integration(models.Model):
    """Base model for all integrations"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_error = models.TextField(blank=True)
    last_error_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.is_enabled:
            self.status = 'inactive'
        super().save(*args, **kwargs)

    def record_error(self, error_message):
        """Record an error for this integration"""
        self.status = 'error'
        self.last_error = error_message
        self.last_error_at = timezone.now()
        self.save()

    def mark_active(self):
        """Mark the integration as active"""
        self.status = 'active'
        self.last_error = ''
        self.last_error_at = None
        self.save()

class IntegrationCredential(models.Model):
    """Store credentials for integrations"""
    
    TYPE_CHOICES = [
        ('api_key', 'API Key'),
        ('secret_key', 'Secret Key'),
        ('access_token', 'Access Token'),
        ('refresh_token', 'Refresh Token'),
        ('certificate', 'Certificate'),
        ('password', 'Password'),
        ('other', 'Other'),
    ]

    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='credentials')
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=500)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_encrypted = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['integration', 'key']
        ordering = ['integration', 'key']

    def __str__(self):
        return f"{self.integration.name} - {self.key}"

    def clean(self):
        """Validate the credential"""
        if self.expires_at and self.expires_at < timezone.now():
            raise ValidationError({
                'expires_at': _('Expiration date cannot be in the past.')
            })

    def is_expired(self):
        """Check if the credential has expired"""
        return self.expires_at and self.expires_at < timezone.now()

class AgoraIntegration(Integration):
    """Agora-specific integration settings"""
    
    app_id = models.CharField(max_length=100, unique=True)
    app_certificate = models.CharField(max_length=100)
    token_expiration_time = models.IntegerField(
        default=3600,
        help_text=_('Token expiration time in seconds')
    )
    max_users_per_channel = models.IntegerField(default=2)
    recording_enabled = models.BooleanField(default=False)
    recording_bucket = models.CharField(
        max_length=200, 
        blank=True,
        help_text=_('S3 bucket for storing recordings')
    )

    def clean(self):
        """Validate Agora settings"""
        if self.recording_enabled and not self.recording_bucket:
            raise ValidationError({
                'recording_bucket': _('Recording bucket is required when recording is enabled.')
            })
        if self.max_users_per_channel < 2:
            raise ValidationError({
                'max_users_per_channel': _('Maximum users per channel must be at least 2.')
            })
        if self.token_expiration_time < 300:  # 5 minutes minimum
            raise ValidationError({
                'token_expiration_time': _('Token expiration time must be at least 300 seconds.')
            })

class IntegrationLog(models.Model):
    """Log integration events and activities"""
    
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('debug', 'Debug'),
    ]

    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='info')
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.integration.name} - {self.level} - {self.created_at}"
