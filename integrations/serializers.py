from rest_framework import serializers
from django.utils import timezone
from .models import Integration, IntegrationCredential, AgoraIntegration, IntegrationLog

class IntegrationCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationCredential
        fields = ['key', 'type', 'expires_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        """Hide the actual value of credentials"""
        ret = super().to_representation(instance)
        ret['is_set'] = bool(instance.value)
        return ret

class IntegrationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationLog
        fields = ['level', 'message', 'metadata', 'created_at']
        read_only_fields = ['created_at']

class IntegrationSerializer(serializers.ModelSerializer):
    credentials = IntegrationCredentialSerializer(many=True, read_only=True)
    recent_logs = serializers.SerializerMethodField()
    
    class Meta:
        model = Integration
        fields = [
            'id', 'name', 'description', 'status', 'is_enabled',
            'created_at', 'updated_at', 'last_error', 'last_error_at',
            'credentials', 'recent_logs'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'last_error', 'last_error_at',
            'credentials', 'recent_logs'
        ]

    def get_recent_logs(self, obj):
        """Get the 5 most recent logs"""
        recent_logs = obj.logs.all()[:5]
        return IntegrationLogSerializer(recent_logs, many=True).data

class AgoraIntegrationSerializer(IntegrationSerializer):
    class Meta(IntegrationSerializer.Meta):
        model = AgoraIntegration
        fields = IntegrationSerializer.Meta.fields + [
            'app_id', 'token_expiration_time', 'max_users_per_channel',
            'recording_enabled', 'recording_bucket'
        ]
        read_only_fields = IntegrationSerializer.Meta.read_only_fields + [
            'app_id'  # app_id should only be set through admin
        ]

    def validate_token_expiration_time(self, value):
        """Validate token expiration time"""
        if value < 300:  # 5 minutes minimum
            raise serializers.ValidationError(
                "Token expiration time must be at least 300 seconds."
            )
        return value

    def validate(self, data):
        """Validate the integration data"""
        if data.get('recording_enabled') and not data.get('recording_bucket'):
            raise serializers.ValidationError({
                'recording_bucket': "Recording bucket is required when recording is enabled."
            })
        return data

class IntegrationStatusSerializer(serializers.ModelSerializer):
    """Simplified serializer for integration status updates"""
    class Meta:
        model = Integration
        fields = ['id', 'status', 'is_enabled', 'last_error']
        read_only_fields = ['id', 'last_error'] 