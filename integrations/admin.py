from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Integration, IntegrationCredential, AgoraIntegration, IntegrationLog

class IntegrationCredentialInline(admin.TabularInline):
    model = IntegrationCredential
    extra = 1
    fields = ('key', 'value', 'type', 'is_encrypted', 'expires_at')
    
class IntegrationLogInline(admin.TabularInline):
    model = IntegrationLog
    extra = 0
    readonly_fields = ('created_at', 'level', 'message', 'metadata', 'user')
    max_num = 0
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'status_badge', 'is_enabled', 'created_at', 'updated_at')
    list_filter = ('status', 'is_enabled')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'last_error_at', 'created_by')
    inlines = [IntegrationCredentialInline, IntegrationLogInline]
    
    def status_badge(self, obj):
        colors = {
            'active': 'success',
            'inactive': 'secondary',
            'error': 'danger'
        }
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(AgoraIntegration)
class AgoraIntegrationAdmin(IntegrationAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_enabled', 'status')
        }),
        (_('Agora Settings'), {
            'fields': ('app_id', 'app_certificate', 'token_expiration_time', 
                      'max_users_per_channel')
        }),
        (_('Recording Settings'), {
            'fields': ('recording_enabled', 'recording_bucket'),
            'classes': ('collapse',)
        }),
        (_('System Fields'), {
            'fields': ('created_at', 'updated_at', 'last_error', 'last_error_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

@admin.register(IntegrationCredential)
class IntegrationCredentialAdmin(admin.ModelAdmin):
    list_display = ('integration', 'key', 'type', 'is_encrypted', 'expires_at', 'created_at')
    list_filter = ('integration', 'type', 'is_encrypted')
    search_fields = ('integration__name', 'key')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('integration')

@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ('integration', 'level', 'message_preview', 'created_at', 'user')
    list_filter = ('integration', 'level', 'created_at')
    search_fields = ('integration__name', 'message')
    readonly_fields = ('created_at',)
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = _('Message')
