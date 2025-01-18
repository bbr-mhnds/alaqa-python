from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'specialist_category', 'slot_time', 'status', 'created_at')
    list_filter = ('status', 'specialist_category', 'gender', 'language')
    search_fields = ('doctor__name', 'phone_number', 'specialist_category')
    readonly_fields = ('video_token', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'slot_time'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('doctor', 'specialties', 'specialist_category', 'gender')
        }),
        ('Appointment Details', {
            'fields': ('duration', 'language', 'phone_number', 'slot_time')
        }),
        ('Status & Video', {
            'fields': ('status', 'video_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    ) 