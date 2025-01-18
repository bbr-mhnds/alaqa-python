from django.contrib import admin
from .models import Drug, DrugCategory, DrugDosageForm


@admin.register(DrugCategory)
class DrugCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "name_arabic", "status", "created_at", "updated_at"]
    list_filter = ["status"]
    search_fields = ["name", "name_arabic"]
    ordering = ["name"]


@admin.register(DrugDosageForm)
class DrugDosageFormAdmin(admin.ModelAdmin):
    list_display = ["name", "name_arabic", "status", "created_at", "updated_at"]
    list_filter = ["status"]
    search_fields = ["name", "name_arabic"]
    ordering = ["name"]


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "name_arabic",
        "category",
        "dosage_form",
        "strength",
        "manufacturer",
        "status",
        "created_at",
        "updated_at",
    ]
    list_filter = ["status", "category", "dosage_form"]
    search_fields = [
        "name",
        "name_arabic",
        "description",
        "description_arabic",
        "manufacturer",
    ]
    ordering = ["name"]
