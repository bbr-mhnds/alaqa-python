from rest_framework import serializers
from .models import InstantAppointmentPrice

class InstantAppointmentPriceSerializer(serializers.ModelSerializer):
    """
    Serializer for InstantAppointmentPrice model
    """
    class Meta:
        model = InstantAppointmentPrice
        fields = ['id', 'duration', 'price', 'site_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_duration(self, value):
        """
        Validate that duration is positive and reasonable
        """
        if value <= 0:
            raise serializers.ValidationError("Duration must be positive")
        if value > 180:  # 3 hours max
            raise serializers.ValidationError("Duration cannot exceed 180 minutes")
        return value

    def validate_price(self, value):
        """
        Validate that price is positive and reasonable
        """
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value

    def validate_site_type(self, value):
        """
        Validate that site_type is one of the allowed values
        """
        allowed_types = ['clinic', 'video', 'home']
        if value.lower() not in allowed_types:
            raise serializers.ValidationError(f"Site type must be one of: {', '.join(allowed_types)}")
        return value.lower() 