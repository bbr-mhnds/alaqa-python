from django.contrib import admin
from .models import Doctor, DoctorVerification, DoctorBankDetails

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
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DoctorVerification)
class DoctorVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'email_verified', 'phone_verified', 'is_used', 'created_at', 'expires_at')
    list_filter = ('email_verified', 'phone_verified', 'is_used', 'created_at')
    search_fields = ('email', 'phone')
    readonly_fields = ('created_at', 'expires_at')
    
    fieldsets = (
        (None, {
            'fields': ('email', 'phone')
        }),
        ('Verification Status', {
            'fields': ('email_verified', 'phone_verified', 'is_used')
        }),
        ('Documents', {
            'fields': ('license_document', 'qualification_document')
        }),
        ('Registration Data', {
            'fields': ('registration_data',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DoctorBankDetails)
class DoctorBankDetailsAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'bank_name', 'account_holder_name', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('doctor__name', 'account_holder_name', 'account_number', 'iban_number')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('doctor', 'bank_name', 'account_holder_name')
        }),
        ('Account Information', {
            'fields': ('account_number', 'iban_number', 'swift_code')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
