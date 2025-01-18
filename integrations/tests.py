from django.test import TestCase, override_settings, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
import json
import hmac
import hashlib
from .models import Integration, IntegrationCredential, AgoraIntegration, IntegrationLog
from .services import AgoraService
import logging
from django.conf import settings
from django.urls import reverse

User = get_user_model()
logger = logging.getLogger(__name__)

class IntegrationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123'
        )
        
        self.integration = Integration.objects.create(
            name='Test Integration',
            description='Test Description',
            is_enabled=True,
            created_by=self.user
        )

    def test_integration_str(self):
        """Test the string representation of Integration"""
        self.assertEqual(
            str(self.integration),
            f"Test Integration (Inactive)"
        )

    def test_record_error(self):
        """Test recording an error"""
        error_message = "Test error message"
        self.integration.record_error(error_message)
        
        self.assertEqual(self.integration.status, 'error')
        self.assertEqual(self.integration.last_error, error_message)
        self.assertIsNotNone(self.integration.last_error_at)

    def test_mark_active(self):
        """Test marking integration as active"""
        self.integration.record_error("Test error")  # First record an error
        self.integration.mark_active()
        
        self.assertEqual(self.integration.status, 'active')
        self.assertEqual(self.integration.last_error, '')
        self.assertIsNone(self.integration.last_error_at)

class AgoraIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123'
        )
        
        self.agora = AgoraIntegration.objects.create(
            name='Agora Integration',
            description='Test Agora',
            is_enabled=True,
            created_by=self.user,
            app_id='test_app_id',
            app_certificate='test_certificate',
            token_expiration_time=3600,
            max_users_per_channel=2
        )

    def test_agora_validation(self):
        """Test Agora integration validation"""
        # Test invalid token expiration time
        self.agora.token_expiration_time = 200
        with self.assertRaises(Exception):
            self.agora.full_clean()
            
        # Test invalid max users
        self.agora.token_expiration_time = 3600
        self.agora.max_users_per_channel = 1
        with self.assertRaises(Exception):
            self.agora.full_clean()
            
        # Test recording validation
        self.agora.max_users_per_channel = 2
        self.agora.recording_enabled = True
        with self.assertRaises(Exception):
            self.agora.full_clean()

class AgoraServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123'
        )
        
        self.agora = AgoraIntegration.objects.create(
            name='Agora Integration',
            description='Test Agora',
            is_enabled=True,
            status='active',
            created_by=self.user,
            app_id='test_app_id',
            app_certificate='test_certificate',
            token_expiration_time=3600,
            max_users_per_channel=2
        )
        
        # Clear cache before each test
        cache.clear()

    def test_get_integration(self):
        """Test getting active integration"""
        integration = AgoraService.get_integration()
        self.assertEqual(integration.id, self.agora.id)
        
        # Test caching
        cached_integration = cache.get(f"{AgoraService.CACHE_KEY_PREFIX}_active")
        self.assertEqual(cached_integration.id, self.agora.id)

    def test_get_integration_no_active(self):
        """Test getting integration when none is active"""
        self.agora.is_enabled = False
        self.agora.save()
        
        integration = AgoraService.get_integration()
        self.assertIsNone(integration)

    @override_settings(
        AGORA_APP_ID='test_app_id',
        AGORA_APP_CERTIFICATE='test_certificate'
    )
    def test_generate_token(self):
        """Test token generation"""
        channel_name = "test_channel"
        uid = 123
        
        token, expiration = AgoraService.generate_token(channel_name, uid)
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        self.assertGreater(expiration, int(timezone.now().timestamp()))
        
        # Check if log was created
        log = IntegrationLog.objects.latest('created_at')
        self.assertEqual(log.level, 'info')
        self.assertEqual(log.integration.id, self.agora.id)

    def test_validate_channel(self):
        """Test channel name validation"""
        # Valid channel name
        self.assertTrue(AgoraService.validate_channel("test_channel"))
        
        # Invalid channel names
        with self.assertRaises(ValueError):
            AgoraService.validate_channel("")
        
        with self.assertRaises(ValueError):
            AgoraService.validate_channel("x" * 65)

    def test_get_settings(self):
        """Test getting integration settings"""
        settings = AgoraService.get_settings()
        
        self.assertEqual(settings['app_id'], self.agora.app_id)
        self.assertEqual(settings['max_users_per_channel'], self.agora.max_users_per_channel)
        self.assertEqual(settings['token_expiration_time'], self.agora.token_expiration_time)
        self.assertEqual(settings['recording_enabled'], self.agora.recording_enabled)

class IntegrationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.agora = AgoraIntegration.objects.create(
            name='Agora Integration',
            description='Test Agora',
            is_enabled=True,
            status='active',
            created_by=self.user,
            app_id='test_app_id',
            app_certificate='test_certificate',
            token_expiration_time=3600,
            max_users_per_channel=2
        )

    def test_list_integrations(self):
        """Test listing integrations"""
        response = self.client.get('/api/v1/integrations/integrations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_toggle_integration(self):
        """Test toggling integration status"""
        url = f'/api/v1/integrations/integrations/{self.agora.id}/toggle/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.agora.refresh_from_db()
        self.assertFalse(self.agora.is_enabled)

    def test_update_agora_settings(self):
        """Test updating Agora settings"""
        url = f'/api/v1/integrations/agora/{self.agora.id}/update_settings/'
        data = {
            'token_expiration_time': 7200,
            'max_users_per_channel': 4
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.agora.refresh_from_db()
        self.assertEqual(self.agora.token_expiration_time, 7200)
        self.assertEqual(self.agora.max_users_per_channel, 4)
        
        # Check if log was created
        log = IntegrationLog.objects.latest('created_at')
        self.assertEqual(log.level, 'info')
        self.assertEqual(log.message, 'Settings updated')

    def test_test_connection(self):
        """Test the connection test endpoint"""
        url = f'/api/v1/integrations/agora/{self.agora.id}/test_connection/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        # Check if log was created
        log = IntegrationLog.objects.latest('created_at')
        self.assertEqual(log.level, 'info')
        self.assertEqual(log.message, 'Successfully tested Agora connection')

class AgoraCallbackTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.callback_url = reverse('agora-callback')
        self.callback_data = {
            'app_id': 'new_app_id',
            'app_certificate': 'new_certificate',
            'credentials': {
                'api_key': 'test_api_key',
                'api_secret': 'test_api_secret'
            },
            'config': {
                'token_expiration_time': 7200,
                'max_users_per_channel': 4,
                'recording_enabled': True,
                'recording_bucket': 'test-bucket'
            }
        }

    def _get_signature(self, data):
        """Helper method to generate signature"""
        payload = json.dumps(data, separators=(',', ':'))
        return hmac.new(
            settings.AGORA_WEBHOOK_SECRET.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    @override_settings(AGORA_WEBHOOK_SECRET='test_secret')
    def test_callback_create_integration(self):
        """Test callback creates new integration when none exists"""
        payload = json.dumps(self.callback_data)
        signature = self._get_signature(self.callback_data)
        
        response = self.client.post(
            self.callback_url,
            data=payload,
            content_type='application/json',
            HTTP_X_AGORA_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode(),
            {'status': 'success', 'message': 'Configuration updated successfully'}
        )
        
        # Check integration was created
        integration = AgoraIntegration.objects.first()
        self.assertIsNotNone(integration)
        self.assertEqual(integration.app_id, 'new_app_id')
        self.assertEqual(integration.app_certificate, 'new_certificate')
        self.assertEqual(integration.token_expiration_time, 7200)
        self.assertTrue(integration.recording_enabled)
        
        # Check credentials were saved
        credentials = IntegrationCredential.objects.filter(integration=integration)
        self.assertEqual(credentials.count(), 2)
        
        # Check log was created
        log = IntegrationLog.objects.latest('created_at')
        self.assertEqual(log.level, 'info')
        self.assertEqual(
            log.message,
            'Successfully updated Agora configuration via callback'
        )

    @override_settings(AGORA_WEBHOOK_SECRET='test_secret')
    def test_callback_update_integration(self):
        """Test callback updates existing integration"""
        # Create existing integration
        integration = AgoraIntegration.objects.create(
            name='Existing Integration',
            description='Test',
            is_enabled=True,
            app_id='old_app_id',
            app_certificate='old_certificate',
            token_expiration_time=3600,
            max_users_per_channel=2
        )
        
        payload = json.dumps(self.callback_data)
        signature = self._get_signature(self.callback_data)
        
        response = self.client.post(
            self.callback_url,
            data=payload,
            content_type='application/json',
            HTTP_X_AGORA_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check integration was updated
        integration.refresh_from_db()
        self.assertEqual(integration.app_id, 'new_app_id')
        self.assertEqual(integration.app_certificate, 'new_certificate')
        self.assertEqual(integration.token_expiration_time, 7200)
        
        # Check new credentials were added
        credentials = IntegrationCredential.objects.filter(integration=integration)
        self.assertEqual(credentials.count(), 2)

    @override_settings(AGORA_WEBHOOK_SECRET='test_secret')
    def test_callback_with_signature(self):
        """Test callback with signature verification"""
        payload = json.dumps(self.callback_data)
        signature = self._get_signature(self.callback_data)
        
        # Test with valid signature
        response = self.client.post(
            self.callback_url,
            data=payload,
            content_type='application/json',
            HTTP_X_AGORA_SIGNATURE=signature
        )
        self.assertEqual(response.status_code, 200)
        
        # Test with invalid signature
        response = self.client.post(
            self.callback_url,
            data=payload,
            content_type='application/json',
            HTTP_X_AGORA_SIGNATURE='invalid_signature'
        )
        self.assertEqual(response.status_code, 401)
        
        # Test without signature
        response = self.client.post(
            self.callback_url,
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    @override_settings(AGORA_WEBHOOK_SECRET='test_secret')
    def test_callback_invalid_json(self):
        """Test callback with invalid JSON data"""
        invalid_data = 'invalid json'
        signature = hmac.new(
            settings.AGORA_WEBHOOK_SECRET.encode(),
            invalid_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        response = self.client.post(
            self.callback_url,
            data=invalid_data,
            content_type='application/json',
            HTTP_X_AGORA_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content.decode(),
            {'error': 'Invalid JSON payload'}
        )
