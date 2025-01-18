from django.contrib import admin
from .models import Prescription, PrescribedDrug, TestRecommendation

class PrescribedDrugInline(admin.TabularInline):
    model = PrescribedDrug
    extra = 1
    autocomplete_fields = ['drug']

class TestRecommendationInline(admin.TabularInline):
    model = TestRecommendation
    extra = 1

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'appointment', 'follow_up_date', 'created_at']
    list_filter = ['created_at', 'follow_up_date']
    search_fields = [
        'appointment__doctor__name',
        'appointment__patient__name',
        'diagnosis'
    ]
    date_hierarchy = 'created_at'
    inlines = [PrescribedDrugInline, TestRecommendationInline]
    autocomplete_fields = ['appointment']

@admin.register(PrescribedDrug)
class PrescribedDrugAdmin(admin.ModelAdmin):
    list_display = [
        'prescription', 'drug', 'dosage',
        'frequency', 'duration', 'duration_unit'
    ]
    list_filter = ['frequency', 'route', 'duration_unit']
    search_fields = ['drug__name', 'prescription__appointment__doctor__name']
    autocomplete_fields = ['prescription', 'drug']

@admin.register(TestRecommendation)
class TestRecommendationAdmin(admin.ModelAdmin):
    list_display = ['prescription', 'test_name', 'urgency', 'created_at']
    list_filter = ['urgency', 'created_at']
    search_fields = [
        'test_name',
        'prescription__appointment__doctor__name'
    ]
    autocomplete_fields = ['prescription'] 