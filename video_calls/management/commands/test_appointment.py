from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from doctors.models import Doctor
from patients.models import Patient
from appointments.models import Appointment
from video_calls.models import VideoCall
from video_calls.views import generate_agora_rtc_token
import time
import random

class Command(BaseCommand):
    help = 'Test appointment and video call flow'

    def handle(self, *args, **options):
        try:
            # Get or create test doctor
            doctor, _ = Doctor.objects.get_or_create(
                email='test.doctor@example.com',
                defaults={
                    'name': 'Test Doctor',
                    'name_arabic': 'طبيب اختبار',
                    'sex': 'male',
                    'phone': '+1234567890',
                    'experience': '10 years',
                    'category': 'consultant',
                    'language_in_sessions': 'english',
                    'license_number': 'TEST123',
                    'profile_arabic': 'نبذة عن الطبيب',
                    'profile_english': 'Doctor profile',
                    'status': 'approved',
                }
            )
            self.stdout.write(f'Using doctor: {doctor.name}')

            # Get or create test patient
            patient, _ = Patient.objects.get_or_create(
                email='test.patient@example.com',
                defaults={
                    'name': 'Test Patient',
                    'name_arabic': 'مريض اختبار',
                    'sex': 'male',
                    'phone': '+1234567890',
                    'date_of_birth': timezone.now().date() - timedelta(days=365*25),
                    'status': 'active'
                }
            )
            self.stdout.write(f'Using patient: {patient.name}')

            # Create video call
            scheduled_time = timezone.now() + timedelta(minutes=5)
            video_call = VideoCall.objects.create(
                doctor=doctor,
                patient=patient,
                scheduled_time=scheduled_time,
                channel_name=f"test_call_{int(time.time())}"
            )
            self.stdout.write(f'Created video call: {video_call.channel_name}')

            # Generate token for video call
            uid = random.randint(1, 230)
            token, expiration_time = generate_agora_rtc_token(video_call.channel_name, uid)
            
            self.stdout.write(self.style.SUCCESS('Successfully created test appointment and video call:'))
            self.stdout.write(f'Channel Name: {video_call.channel_name}')
            self.stdout.write(f'UID: {uid}')
            self.stdout.write(f'Token: {token}')
            self.stdout.write(f'Expiration: {expiration_time}')
            self.stdout.write(f'Scheduled Time: {scheduled_time}')
            
            # Test joining the call
            can_join, error = video_call.can_join()
            if can_join:
                self.stdout.write(self.style.SUCCESS('Call can be joined'))
                # Start the call
                if video_call.start_call():
                    self.stdout.write(self.style.SUCCESS('Call started successfully'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to start call'))
            else:
                self.stdout.write(self.style.ERROR(f'Cannot join call: {error}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in test: {str(e)}')) 