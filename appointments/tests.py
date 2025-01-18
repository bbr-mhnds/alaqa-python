from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
from unittest.mock import patch
from doctors.models import Doctor
from specialties.models import Specialty
from authentication.models import User
from .models import Appointment

class AppointmentTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_active=True,
            is_verified=True
        )
        
        # Create a specialty
        self.specialty = Specialty.objects.create(
            title='Test Specialty',
            title_ar='تخصص اختبار',
            icon='test-icon',
            background_color='#ffffff',
            color_class='bg-primary',
            description='Test Description',
            description_ar='وصف الاختبار',
            total_time_call=30,
            warning_time_call=5,
            alert_time_call=2
        )
        
        # Create a doctor
        self.doctor = Doctor.objects.create(
            name='Dr. Test',
            name_arabic='د. اختبار',
            sex='male',
            email='doctor@test.com',
            phone='+1234567890',
            experience='10 years',
            category='consultant',
            language_in_sessions='english',
            license_number='TEST123',
            profile_arabic='نبذة عن الطبيب',
            profile_english='Doctor profile',
            status='approved'
        )
        self.doctor.specialities.add(self.specialty)
        
        # Set up authentication
        self.client.force_authenticate(user=self.user)
        
        # Base appointment data
        self.appointment_data = {
            'doctor': self.doctor.id,
            'specialties': [self.specialty.id],
            'specialist_category': 'Test Category',
            'gender': 'M',
            'duration': '30',
            'language': 'English',
            'phone_number': '1234567890',
            'slot_time': (timezone.now() + timedelta(days=1)).isoformat()
        }

    @patch('requests.post')
    def test_create_appointment(self, mock_post):
        """Test creating a new appointment"""
        # Mock the video token response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'data': {'token': 'test_token_123'}
        }
        
        response = self.client.post('/api/v1/appointments/', self.appointment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(response.data['video_token'], 'test_token_123')

    def test_list_appointments(self):
        """Test listing appointments"""
        # Create some test appointments
        Appointment.objects.create(
            doctor=self.doctor,
            specialist_category='Test Category',
            gender='M',
            duration='30',
            language='English',
            phone_number='1234567890',
            slot_time=timezone.now() + timedelta(days=1),
            video_token='test_token'
        )
        
        response = self.client.get('/api/v1/appointments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_appointments(self):
        """Test filtering appointments by doctor and status"""
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            specialist_category='Test Category',
            gender='M',
            duration='30',
            language='English',
            phone_number='1234567890',
            slot_time=timezone.now() + timedelta(days=1),
            video_token='test_token'
        )
        
        # Test filtering by doctor
        response = self.client.get(f'/api/v1/appointments/?doctor_id={self.doctor.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtering by status
        response = self.client.get('/api/v1/appointments/?status=SCHEDULED')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_cancel_appointment(self):
        """Test cancelling an appointment"""
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            specialist_category='Test Category',
            gender='M',
            duration='30',
            language='English',
            phone_number='1234567890',
            slot_time=timezone.now() + timedelta(days=1),
            video_token='test_token'
        )
        
        response = self.client.post(f'/api/v1/appointments/{appointment.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'CANCELLED')

    @patch('requests.post')
    def test_failed_token_generation(self, mock_post):
        """Test handling failed token generation"""
        # Mock a failed token response
        mock_post.return_value.status_code = 500
        mock_post.return_value.json.return_value = {'error': 'Token generation failed'}
        
        response = self.client.post('/api/v1/appointments/', self.appointment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)

class AppointmentModelTests(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            name='Dr. Test',
            name_arabic='د. اختبار',
            sex='male',
            email='doctor@test.com',
            phone='+1234567890',
            experience='10 years',
            category='consultant',
            language_in_sessions='english',
            license_number='TEST123',
            profile_arabic='نبذة عن الطبيب',
            profile_english='Doctor profile',
            status='approved'
        )

    def test_appointment_str_representation(self):
        """Test the string representation of an Appointment"""
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            specialist_category='Test Category',
            gender='M',
            duration='30',
            language='English',
            phone_number='1234567890',
            slot_time=timezone.now() + timedelta(days=1),
            video_token='test_token'
        )
        expected_str = f"Appointment with Dr. {self.doctor.name} at {appointment.slot_time}"
        self.assertEqual(str(appointment), expected_str) 