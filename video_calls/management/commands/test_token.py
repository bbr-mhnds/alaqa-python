from django.core.management.base import BaseCommand
from video_calls.views import generate_agora_rtc_token
import time
import random

class Command(BaseCommand):
    help = 'Test Agora token generation'

    def handle(self, *args, **options):
        try:
            # Generate test channel name
            timestamp = int(time.time())
            channel_name = f"test_channel_{timestamp}"
            
            # Generate test UID
            timestamp_part = int(str(timestamp)[-4:])
            random_part = random.randint(1, 999)
            uid = int(f"{timestamp_part}{random_part}")

            # Generate token
            token, expiration_time = generate_agora_rtc_token(channel_name, uid)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully generated token:'))
            self.stdout.write(f'Channel: {channel_name}')
            self.stdout.write(f'UID: {uid}')
            self.stdout.write(f'Token: {token}')
            self.stdout.write(f'Expiration: {expiration_time}')
            
            # Verify token format
            if not token.startswith('006'):
                self.stdout.write(self.style.WARNING('Warning: Token does not start with 006'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating token: {str(e)}')) 