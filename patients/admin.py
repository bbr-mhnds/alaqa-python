from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_arabic', 'email', 'phone', 'status', 'updated_at')
    list_filter = ('status', 'sex')
    search_fields = ('name', 'name_arabic', 'email', 'phone')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
