import uuid
from django.db import models
from django.utils import timezone
from doctors.models import Doctor
from patients.models import Patient

class VideoCall(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel_name = models.CharField(max_length=255, unique=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='video_calls')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='video_calls')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    scheduled_time = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_time']
        verbose_name = 'Video Call'
        verbose_name_plural = 'Video Calls'

    def __str__(self):
        return f"Call between {self.doctor} and {self.patient} at {self.scheduled_time}"

    def start_call(self):
        """Start the video call"""
        if self.status != 'scheduled':
            return False
        self.status = 'ongoing'
        self.started_at = timezone.now()
        self.save()
        return True

    def mark_completed(self):
        """Mark the call as completed"""
        if self.status != 'ongoing':
            return False
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.save()
        return True

    def mark_cancelled(self):
        """Cancel the call"""
        if self.status != 'scheduled':
            return False
        self.status = 'cancelled'
        self.save()
        return True

    def get_duration(self):
        """Get the duration of the call in seconds"""
        if not self.started_at:
            return 0
        end_time = self.ended_at or timezone.now()
        return int((end_time - self.started_at).total_seconds())

    def is_expired(self):
        """Check if the call has expired"""
        return self.scheduled_time < timezone.now() - timezone.timedelta(minutes=30)

    def can_join(self):
        """Check if the call can be joined"""
        if self.status == 'cancelled':
            return False, "Call has been cancelled"
        if self.status == 'completed':
            return False, "Call has already ended"
        if self.status == 'scheduled' and self.is_expired():
            return False, "Call has expired"
        return True, None
