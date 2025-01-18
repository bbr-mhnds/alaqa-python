from django.contrib import admin
from .models import InstantAppointmentPrice

@admin.register(InstantAppointmentPrice)
class InstantAppointmentPriceAdmin(admin.ModelAdmin):
    """
    Admin configuration for InstantAppointmentPrice model
    """
    list_display = ('duration', 'price', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('duration', 'price')
    ordering = ('duration',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('duration', 'price')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
