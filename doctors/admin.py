from django.contrib import admin
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'license_number', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'specialities', 'created_at')
    search_fields = ('name', 'name_arabic', 'email', 'phone', 'license_number')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('specialities',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'name_arabic', 'sex', 'email', 'phone')
        }),
        ('Professional Information', {
            'fields': ('experience', 'category', 'language_in_sessions', 'license_number', 'specialities')
        }),
        ('Profile', {
            'fields': ('profile_arabic', 'profile_english', 'photo')
        }),
        ('Bank Details', {
            'fields': ('account_holder_name', 'account_number', 'iban_number')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
