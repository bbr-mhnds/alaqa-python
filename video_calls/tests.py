from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from datetime import datetime, timedelta
from authentication.models import User
from doctors.models import Doctor
from patients.models import Patient
from integrations.models import AgoraIntegration
from .models import VideoCall

@override_settings(
    AGORA_APP_ID='test_app_id',
    AGORA_APP_CERTIFICATE='test_certificate'
)
class VideoCallTests(APITestCase):
    def setUp(self):
        # Create Agora integration
        self.agora_integration = AgoraIntegration.objects.create(
            app_id='test_app_id',
            app_certificate='test_certificate',
            is_enabled=True,
            status='active',
            token_expiration_time=3600  # 1 hour
        )

        # Create a doctor user
        self.doctor_user = User.objects.create_user(
            email='doctor@test.com',
            password='testpass123',
            first_name='Doctor',
            last_name='Test',
            is_active=True,
            is_verified=True
        )

        # Create a doctor profile
        self.doctor = Doctor.objects.create(
            name='Dr. Test Doctor',
            name_arabic='د. طبيب اختبار',
            sex='male',
            email=self.doctor_user.email,
            phone='+1234567890',
            experience='10 years',
            category='consultant',
            language_in_sessions='english',
            license_number='TEST123',
            profile_arabic='نبذة عن الطبيب',
            profile_english='Doctor profile',
            status='approved',
            account_holder_name='Test Doctor',
            account_number='1234567890',
            iban_number='SA1234567890'
        )

        # Create a patient user
        self.patient_user = User.objects.create_user(
            email='patient@test.com',
            password='testpass123',
            first_name='Patient',
            last_name='Test',
            is_active=True,
            is_verified=True
        )

        # Create a patient profile
        self.patient = Patient.objects.create(
            name='Test Patient',
            name_arabic='مريض اختبار',
            sex='male',
            email=self.patient_user.email,
            phone='+1234567890',
            date_of_birth=timezone.now().date() - timedelta(days=365*25),
            status='active'
        )

        # Create a scheduled time in the future
        self.scheduled_time = timezone.now() + timedelta(minutes=5)
        
        # Create a video call
        self.video_call = VideoCall.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            scheduled_time=self.scheduled_time,
            channel_name=f"test_call_{timezone.now().timestamp()}"
        )

    def test_create_video_call(self):
        """Test creating a new video call"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('video-calls-list')
        data = {
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'scheduled_time': (timezone.now() + timedelta(hours=2)).isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(VideoCall.objects.filter(id=response.data['id']).exists())
        self.assertIsNotNone(response.data.get('channel_name'))

    def test_list_video_calls_as_doctor(self):
        """Test listing video calls as a doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('video-calls-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_video_calls_as_patient(self):
        """Test listing video calls as a patient"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('video-calls-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_join_video_call_as_doctor(self):
        """Test joining a video call as a doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('video-calls-join', kwargs={'pk': self.video_call.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('channel_name', response.data)
        self.assertIn('token', response.data)
        self.assertIn('uid', response.data)
        self.assertIn('expiration_time', response.data)

    def test_join_video_call_as_patient(self):
        """Test joining a video call as a patient"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('video-calls-join', kwargs={'pk': self.video_call.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('channel_name', response.data)
        self.assertIn('token', response.data)
        self.assertIn('uid', response.data)
        self.assertIn('expiration_time', response.data)

    def test_end_video_call(self):
        """Test ending a video call"""
        # First join the call to make it active
        self.video_call.status = 'ongoing'
        self.video_call.started_at = timezone.now()
        self.video_call.save()

        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('video-calls-end', kwargs={'pk': self.video_call.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.video_call.refresh_from_db()
        self.assertEqual(self.video_call.status, 'completed')
        self.assertIsNotNone(self.video_call.ended_at)

    def test_cancel_scheduled_call(self):
        """Test cancelling a scheduled call"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('video-calls-cancel', kwargs={'pk': self.video_call.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.video_call.refresh_from_db()
        self.assertEqual(self.video_call.status, 'cancelled')

    def test_cancel_ongoing_call(self):
        """Test attempting to cancel an ongoing call"""
        self.video_call.status = 'ongoing'
        self.video_call.save()

        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('video-calls-cancel', kwargs={'pk': self.video_call.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_join_cancelled_call(self):
        """Test attempting to join a cancelled call"""
        self.video_call.status = 'cancelled'
        self.video_call.save()

        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('video-calls-join', kwargs={'pk': self.video_call.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_join_completed_call(self):
        """Test attempting to join a completed call"""
        self.video_call.status = 'completed'
        self.video_call.save()

        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('video-calls-join', kwargs={'pk': self.video_call.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_overlapping_call(self):
        """Test creating a call that overlaps with an existing one"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('video-calls-list')
        data = {
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'scheduled_time': self.scheduled_time.isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_access(self):
        """Test unauthorized access to video calls"""
        # Create another user who is not part of the call
        other_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123',
            first_name='Other',
            last_name='User',
            is_active=True,
            is_verified=True
        )
        other_patient = Patient.objects.create(
            name='Other Patient',
            name_arabic='مريض آخر',
            sex='male',
            email=other_user.email,
            phone='+1234567890',
            date_of_birth=timezone.now().date() - timedelta(days=365*30),
            status='active'
        )
        self.client.force_authenticate(user=other_user)
        
        # Try to join the call
        url = reverse('video-calls-join', kwargs={'pk': self.video_call.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_call_end(self):
        """Test ending a call that is not ongoing"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('video-calls-end', kwargs={'pk': self.video_call.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_access(self):
        """Test accessing endpoints without authentication"""
        # Try to list calls
        url = reverse('video-calls-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try to join a call
        url = reverse('video-calls-join', kwargs={'pk': self.video_call.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_call_with_past_time(self):
        """Test creating a call with a past scheduled time"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('video-calls-list')
        data = {
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'scheduled_time': (timezone.now() - timedelta(hours=1)).isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_token_authenticated(self):
        """Test generating Agora token as authenticated user"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('generate-token')
        data = {
            'channel_name': self.video_call.channel_name,
            'role': 1  # Publisher role
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data['data'])
        self.assertIn('channel', response.data['data'])
        self.assertIn('uid', response.data['data'])
        self.assertIn('app_id', response.data['data'])

    def test_generate_token_unauthenticated(self):
        """Test generating Agora token without authentication"""
        url = reverse('generate-token')
        data = {
            'channel_name': self.video_call.channel_name,
            'role': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_generate_token_invalid_channel(self):
        """Test generating token with invalid channel name"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('generate-token')
        data = {
            'channel_name': 'ab',  # Too short, minimum is 3 characters
            'role': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_token_missing_channel(self):
        """Test generating token without channel name"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('generate-token')
        data = {
            'role': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
