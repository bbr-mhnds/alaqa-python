from rest_framework import serializers
from .models import Specialty

class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = [
            'id', 'title', 'title_ar', 'icon', 'background_color',
            'color_class', 'description', 'description_ar',
            'total_time_call', 'warning_time_call', 'alert_time_call',
            'status', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']

    def validate(self, data):
        # Validate time calls
        total_time = data.get('total_time_call', 0)
        warning_time = data.get('warning_time_call', 0)
        alert_time = data.get('alert_time_call', 0)

        if warning_time >= total_time:
            raise serializers.ValidationError({
                'warning_time_call': 'Warning time must be less than total time'
            })

        if alert_time >= warning_time:
            raise serializers.ValidationError({
                'alert_time_call': 'Alert time must be less than warning time'
            })

        return data

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Title must be at least 3 characters long')
        return value

    def validate_title_ar(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Arabic title must be at least 3 characters long')
        return value 