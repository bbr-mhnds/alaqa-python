from django.db import models
import uuid

class Specialty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)
    background_color = models.CharField(max_length=50)
    color_class = models.CharField(max_length=50)
    description = models.TextField()
    description_ar = models.TextField()
    total_time_call = models.IntegerField()
    warning_time_call = models.IntegerField()
    alert_time_call = models.IntegerField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Specialty'
        verbose_name_plural = 'Specialties'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
