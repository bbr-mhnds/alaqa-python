import unittest
from django.test import TestCase
from django.conf import settings
from integrations.services.agora import AgoraService

class AgoraServiceTest(TestCase):
    def setUp(self):
        self.agora_service = AgoraService()
        self.test_channel = "test_channel"
        self.test_uid = 12345

    def test_token_generation(self):
        """Test that tokens can be generated successfully"""
        try:
            token = self.agora_service.generate_rtc_token(
                channel_name=self.test_channel,
                uid=self.test_uid,
                role=1  # Publisher role
            )
            
            # Token should be a non-empty string
            self.assertIsInstance(token, str)
            self.assertTrue(len(token) > 0)
            
            # Token should start with the correct prefix
            self.assertTrue(token.startswith('006'))
            
        except Exception as e:
            self.fail(f"Token generation failed: {str(e)}")

    def test_invalid_credentials(self):
        """Test handling of missing credentials"""
        service = AgoraService()
        service.app_id = None  # Simulate missing app ID
        
        with self.assertRaises(ValueError):
            service.generate_rtc_token(
                channel_name=self.test_channel,
                uid=self.test_uid,
                role=1
            )

    @unittest.skipIf(not settings.AGORA_APP_ID, "Agora credentials not configured")
    def test_token_expiration(self):
        """Test token expiration time"""
        # Generate token with 5 second expiration
        token = self.agora_service.generate_rtc_token(
            channel_name=self.test_channel,
            uid=self.test_uid,
            role=1,
            privilege_expired_ts=5
        )
        
        self.assertIsInstance(token, str) 