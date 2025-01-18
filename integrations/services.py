import logging
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime
from agora_token_builder import RtcTokenBuilder
from .models import AgoraIntegration, IntegrationLog

logger = logging.getLogger(__name__)

class AgoraService:
    """Service class for handling Agora integration"""
    
    CACHE_KEY_PREFIX = 'agora_integration'
    CACHE_TIMEOUT = 300  # 5 minutes
    
    @classmethod
    def get_integration(cls, cache_enabled=True):
        """Get the active Agora integration"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}_active"
        
        if cache_enabled:
            cached_integration = cache.get(cache_key)
            if cached_integration:
                return cached_integration
        
        try:
            integration = AgoraIntegration.objects.filter(
                is_enabled=True,
                status='active'
            ).latest('created_at')
            
            if cache_enabled:
                cache.set(cache_key, integration, cls.CACHE_TIMEOUT)
            
            return integration
        except AgoraIntegration.DoesNotExist:
            return None

    @classmethod
    def generate_token(cls, channel_name, uid, role=1):  # 1 is publisher role
        """Generate an Agora token"""
        integration = cls.get_integration()
        if not integration:
            raise ValueError("No active Agora integration found")
        
        try:
            # Generate token
            expiration_time_in_seconds = integration.token_expiration_time
            current_timestamp = int(timezone.now().timestamp())
            privilegeExpiredTs = current_timestamp + expiration_time_in_seconds
            
            token = RtcTokenBuilder.buildTokenWithUid(
                str(integration.app_id),
                str(integration.app_certificate),
                channel_name,
                uid,
                role,
                privilegeExpiredTs
            )
            
            # Log success
            IntegrationLog.objects.create(
                integration=integration,
                level='info',
                message=f'Generated token for channel: {channel_name}',
                metadata={
                    'channel_name': channel_name,
                    'uid': str(uid),
                    'expiration': datetime.fromtimestamp(privilegeExpiredTs).isoformat()
                }
            )
            
            return token, privilegeExpiredTs
            
        except Exception as e:
            error_message = f"Failed to generate Agora token: {str(e)}"
            logger.error(error_message, exc_info=True)
            
            # Log error
            IntegrationLog.objects.create(
                integration=integration,
                level='error',
                message=error_message
            )
            
            integration.record_error(error_message)
            raise

    @classmethod
    def validate_channel(cls, channel_name):
        """Validate a channel name"""
        integration = cls.get_integration()
        if not integration:
            raise ValueError("No active Agora integration found")
            
        # Add any channel-specific validation here
        if not channel_name or len(channel_name) > 64:
            raise ValueError("Invalid channel name")
            
        return True

    @classmethod
    def get_settings(cls):
        """Get Agora settings"""
        integration = cls.get_integration()
        if not integration:
            raise ValueError("No active Agora integration found")
            
        return {
            'app_id': integration.app_id,
            'max_users_per_channel': integration.max_users_per_channel,
            'token_expiration_time': integration.token_expiration_time,
            'recording_enabled': integration.recording_enabled,
            'recording_bucket': integration.recording_bucket if integration.recording_enabled else None
        }

    @classmethod
    def clear_cache(cls):
        """Clear the integration cache"""
        cache.delete(f"{cls.CACHE_KEY_PREFIX}_active") 