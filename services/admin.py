from django.contrib import admin
from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['name_en', 'name_ar', 'description_en', 'description_ar']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('is_active',)
        }),
        ('English Content', {
            'fields': ('name_en', 'description_en')
        }),
        ('Arabic Content', {
            'fields': ('name_ar', 'description_ar')
        }),
        ('Media', {
            'fields': ('icon',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
