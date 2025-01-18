import os
import time
import logging
from django.conf import settings
from agora_token_builder import RtcTokenBuilder

logger = logging.getLogger(__name__)

class AgoraService:
    def __init__(self):
        self.app_id = settings.AGORA_APP_ID
        self.app_certificate = settings.AGORA_APP_CERTIFICATE
        
    def generate_rtc_token(self, channel_name, uid, role, privilege_expired_ts=3600):
        """
        Generate an RTC token for video calling
        
        Args:
            channel_name (str): The channel name for the video call
            uid (int): User ID 
            role (int): Role type (1 for publisher, 2 for subscriber)
            privilege_expired_ts (int): Token expiration time in seconds
            
        Returns:
            str: Generated token
        """
        try:
            if not all([self.app_id, self.app_certificate, channel_name]):
                raise ValueError("Missing required Agora credentials")

            # Calculate expiration time
            expiration_time = int(time.time()) + privilege_expired_ts
            
            # Generate the token
            token = RtcTokenBuilder.buildTokenWithUid(
                self.app_id,
                self.app_certificate,
                channel_name,
                uid,
                role,
                expiration_time
            )
            
            logger.info(f"Generated Agora token for channel: {channel_name}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating Agora token: {str(e)}")
            raise 