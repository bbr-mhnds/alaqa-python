from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import timedelta
import json

from doctors.models import Doctor
from appointments.models import Appointment
from django.contrib.auth import get_user_model

User = get_user_model()

class AppointmentCompletionTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        # Create a doctor user
        self.doctor_user = User.objects.create_user(
            email='doctor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Doctor'
        )
        
        # Create another doctor user for unauthorized tests
        self.other_doctor_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123',
            first_name='Other',
            last_name='Doctor'
        )

        # Create doctor profiles
        self.doctor = Doctor.objects.create(
            email=self.doctor_user.email,
            name="Dr. Test",
            name_arabic="د. تجربة",
            sex='male',
            phone="+1234567890",
            experience="10 years",
            category="specialist",
            language_in_sessions="english",
            license_number="LIC123456",
            profile_arabic="نبذة عن الطبيب",
            profile_english="Doctor profile",
            status="approved"
        )
        
        self.other_doctor = Doctor.objects.create(
            email=self.other_doctor_user.email,
            name="Dr. Other",
            name_arabic="د. آخر",
            sex='female',
            phone="+9876543210",
            experience="5 years",
            category="specialist",
            language_in_sessions="english",
            license_number="LIC654321",
            profile_arabic="نبذة عن الطبيب الآخر",
            profile_english="Other doctor profile",
            status="approved"
        )

        # Create a scheduled appointment
        self.slot_time = timezone.now() + timedelta(hours=1)
        self.appointment = Appointment.objects.create(
            doctor=self.doctor,
            status='SCHEDULED',
            slot_time=self.slot_time,
            specialist_category='General',
            patient_id='PAT123',
            gender='M',
            duration='30',
            language='english',
            phone_number='1234567890'
        )

        # URL for completing appointment
        self.complete_url = reverse('appointment-complete', kwargs={'appointment_id': self.appointment.id})

        # Valid completion data
        self.valid_completion_data = {
            'completion_notes': 'Test completion notes',
            'duration_minutes': 30,
            'completion_time': (self.slot_time + timedelta(minutes=30)).isoformat()
        }

    def test_complete_appointment_success(self):
        """Test successful appointment completion"""
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.post(self.complete_url, self.valid_completion_data, format='json')
        
        if response.status_code != status.HTTP_200_OK:
            print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        # Verify appointment was updated
        appointment = Appointment.objects.get(id=self.appointment.id)
        self.assertEqual(appointment.status, 'COMPLETED')
        self.assertEqual(appointment.completion_notes, self.valid_completion_data['completion_notes'])
        self.assertEqual(appointment.duration_minutes, self.valid_completion_data['duration_minutes'])

    def test_complete_appointment_unauthorized(self):
        """Test appointment completion by unauthorized doctor"""
        self.client.force_authenticate(user=self.other_doctor_user)
        response = self.client.post(self.complete_url, self.valid_completion_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_complete_appointment_unauthenticated(self):
        """Test appointment completion without authentication"""
        response = self.client.post(self.complete_url, self.valid_completion_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_complete_nonexistent_appointment(self):
        """Test completing non-existent appointment"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('appointment-complete', kwargs={'appointment_id': 99999})
        response = self.client.post(url, self.valid_completion_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_complete_already_completed_appointment(self):
        """Test completing an already completed appointment"""
        self.appointment.status = 'COMPLETED'
        self.appointment.save()
        
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.post(self.complete_url, self.valid_completion_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_complete_cancelled_appointment(self):
        """Test completing a cancelled appointment"""
        self.appointment.status = 'CANCELLED'
        self.appointment.save()
        
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.post(self.complete_url, self.valid_completion_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_complete_appointment_future_completion_time(self):
        """Test completion with future completion time"""
        self.client.force_authenticate(user=self.doctor_user)
        future_data = self.valid_completion_data.copy()
        future_data['completion_time'] = (timezone.now() + timedelta(days=1)).isoformat()
        
        response = self.client.post(self.complete_url, future_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Completion time cannot be in the future', response.data['message'])

    def test_complete_appointment_before_scheduled_time(self):
        """Test completion time before scheduled time"""
        self.client.force_authenticate(user=self.doctor_user)
        invalid_data = self.valid_completion_data.copy()
        invalid_data['completion_time'] = (self.slot_time - timedelta(hours=1)).isoformat()
        
        response = self.client.post(self.complete_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Completion time must be after scheduled time', response.data['message'])

    def test_complete_appointment_invalid_duration(self):
        """Test completion with invalid duration"""
        self.client.force_authenticate(user=self.doctor_user)
        invalid_data = self.valid_completion_data.copy()
        invalid_data['duration_minutes'] = 0
        
        response = self.client.post(self.complete_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Duration minutes must be greater than 0', response.data['message'])

    def test_complete_appointment_missing_all_fields(self):
        """Test completion with empty data"""
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.post(self.complete_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complete_appointment_partial_data(self):
        """Test completion with partial data"""
        self.client.force_authenticate(user=self.doctor_user)
        partial_data = {
            'completion_notes': 'Only notes provided'
        }
        
        response = self.client.post(self.complete_url, partial_data, format='json')
        
        if response.status_code != status.HTTP_200_OK:
            print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        # Verify appointment was updated with partial data
        appointment = Appointment.objects.get(id=self.appointment.id)
        self.assertEqual(appointment.status, 'COMPLETED')
        self.assertEqual(appointment.completion_notes, partial_data['completion_notes'])
        self.assertIsNotNone(appointment.completion_time)  # Should use default current time 