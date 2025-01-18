from django.contrib import admin
from django.utils.html import format_html
from .models import OTP

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp_code', 'status_badge', 'remaining_time', 'attempts_display', 'created_at')
    list_filter = (
        ('is_verified', admin.BooleanFieldListFilter),
        ('attempts', admin.ChoicesFieldListFilter),
        ('created_at', admin.DateFieldListFilter),
    )
    search_fields = ('phone_number', 'otp_code')
    readonly_fields = ('id', 'created_at', 'expires_at', 'attempts', 'remaining_time', 'status_display')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('OTP Information', {
            'fields': ('id', 'phone_number', 'otp_code', 'status_display', 'is_verified')
        }),
        ('Status Information', {
            'fields': ('attempts', 'remaining_time', 'created_at', 'expires_at')
        }),
    )
    
    def status_badge(self, obj):
        """Display status as a colored badge"""
        status = obj.get_status_display()
        color = {
            'Verified': 'success',
            'Expired': 'danger',
            'Max Attempts': 'warning',
            'Active': 'primary'
        }.get(status, 'secondary')
            
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>',
            {
                'success': '#28a745',
                'danger': '#dc3545',
                'warning': '#ffc107',
                'primary': '#007bff',
                'secondary': '#6c757d'
            }[color],
            status
        )
    status_badge.short_description = 'Status'
    
    def remaining_time(self, obj):
        """Display remaining time with color coding"""
        time_str = obj.get_remaining_time()
        if time_str == "Expired":
            color = "#dc3545"  # Red
        else:
            color = "#28a745"  # Green
        return format_html('<span style="color: {};">{}</span>', color, time_str)
    remaining_time.short_description = 'Remaining Time'
    
    def attempts_display(self, obj):
        """Display attempts with color coding"""
        attempts = obj.attempts
        if attempts >= 3:
            color = "#dc3545"  # Red
        elif attempts >= 2:
            color = "#ffc107"  # Yellow
        else:
            color = "#28a745"  # Green
        return format_html('<span style="color: {};">{}</span>', color, obj.get_attempts_display())
    attempts_display.short_description = 'Attempts'
    
    def status_display(self, obj):
        """Display status for detail view"""
        return self.status_badge(obj)
    status_display.short_description = 'Status'
    
    def has_add_permission(self, request):
        """Disable manual OTP creation"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of OTP records"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting OTP records"""
        return True
