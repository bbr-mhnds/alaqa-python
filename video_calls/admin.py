from django.contrib import admin
from .models import VideoCall

@admin.register(VideoCall)
class VideoCallAdmin(admin.ModelAdmin):
    list_display = ('channel_name', 'doctor', 'patient', 'status', 'scheduled_time', 'duration', 'created_at')
    list_filter = ('status', 'scheduled_time', 'created_at')
    search_fields = ('channel_name', 'doctor__name', 'patient__name')
    readonly_fields = ('created_at', 'updated_at', 'duration')
    ordering = ('-scheduled_time',)

    fieldsets = (
        (None, {
            'fields': ('channel_name', 'doctor', 'patient', 'status')
        }),
        ('Timing', {
            'fields': ('scheduled_time', 'started_at', 'ended_at')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at', 'duration'),
            'classes': ('collapse',)
        }),
    )

    def duration(self, obj):
        duration = obj.get_duration()
        return f"{duration} minutes" if duration else "N/A"
    duration.short_description = "Call Duration"

    def has_add_permission(self, request):
        # Calls should be created through the API only
        return False
