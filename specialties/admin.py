from django.contrib import admin
from .models import Specialty

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('title', 'title_ar', 'status', 'updated_at')
    list_filter = ('status',)
    search_fields = ('title', 'title_ar', 'description', 'description_ar')
    readonly_fields = ('id', 'created_at', 'updated_at')
