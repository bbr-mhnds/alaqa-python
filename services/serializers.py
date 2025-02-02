from rest_framework import serializers
from .models import Service

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'id',
            'name_en',
            'name_ar',
            'description_en',
            'description_ar',
            'icon',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_icon(self, value):
        if value.size > 2 * 1024 * 1024:  # 2MB limit
            raise serializers.ValidationError("Icon file size cannot exceed 2MB")
        return value 