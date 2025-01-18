import os
import django
from django.core.management import call_command
from django.contrib.auth import get_user_model
from doctors.models import Doctor
from patients.models import Patient
from video_calls.models import VideoCall
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def setup_test_data():
    print("Setting up test data...")
    
    # Create test users
    User = get_user_model()
    
    # Create doctor
    doctor_user = User.objects.create_user(
        email='doctor@test.com',
        password='test123',
        first_name='Test',
        last_name='Doctor'
    )
    doctor = Doctor.objects.create(
        user=doctor_user,
        name='Dr. Test Doctor',
        email='doctor@test.com',
        phone='+1234567890',
        license_number='TEST123',
        status='approved'
    )
    
    # Create patient
    patient_user = User.objects.create_user(
        email='patient@test.com',
        password='test123',
        first_name='Test',
        last_name='Patient'
    )
    patient = Patient.objects.create(
        user=patient_user,
        name='Test Patient',
        email='patient@test.com',
        phone='+1234567891',
        status='active'
    )
    
    # Create video call
    video_call = VideoCall.objects.create(
        channel_name='test_channel_1',
        doctor=doctor,
        patient=patient,
        scheduled_time=timezone.now() + timedelta(hours=1),
        status='scheduled'
    )
    
    print("Test data created successfully!")
    return doctor, patient, video_call

def test_agora_integration():
    print("\nTesting Agora integration...")
    
    # Test token generation
    call_command('test_agora', 'test_channel_1', '--uid=12345')
    
    # Run Agora tests
    call_command('test', 'video_calls.tests.test_agora')

if __name__ == '__main__':
    # Setup test data
    doctor, patient, video_call = setup_test_data()
    
    # Test Agora integration
    test_agora_integration() 