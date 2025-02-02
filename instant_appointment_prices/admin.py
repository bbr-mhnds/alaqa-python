from django.contrib import admin
from .models import InstantAppointmentPrice
from rest_framework import serializers

@admin.register(InstantAppointmentPrice)
class InstantAppointmentPriceAdmin(admin.ModelAdmin):
    """
    Admin configuration for InstantAppointmentPrice model
    """
    list_display = ('duration', 'price', 'site_type', 'created_at', 'updated_at')
    list_filter = ('created_at', 'site_type')
    search_fields = ('duration', 'price', 'site_type')
    ordering = ('site_type', 'duration')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('duration', 'price', 'site_type')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def validate_swift_code(self, value):
        """
        Validate SWIFT/BIC code format
        """
        if value:
            # Remove spaces and convert to uppercase
            value = value.replace(' ', '').upper()
            # SWIFT code should be either 8 or 11 characters
            if len(value) not in [8, 11]:
                raise serializers.ValidationError("SWIFT code must be either 8 or 11 characters long")
            # Basic format validation (4 letters for bank code, 2 letters for country code, etc.)
            if not (value[:4].isalpha() and value[4:6].isalpha()):
                raise serializers.ValidationError("Invalid SWIFT code format")
        return value

    @property
    def bank_details(self):
        return {
            'bank_name': self.bank_name,
            'account_holder_name': self.account_holder_name,
            'account_number': self.account_number,
            'iban_number': self.iban_number,
            'swift_code': self.swift_code
        }
