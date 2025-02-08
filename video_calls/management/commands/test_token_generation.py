from django.core.management.base import BaseCommand
from video_calls.token_builder import AgoraTokenBuilder
from django.conf import settings
import time

class Command(BaseCommand):
    help = 'Test the custom Agora token generation'

    def handle(self, *args, **options):
        try:
            # Test parameters
            channel_name = "test_channel"
            uid = 12345
            role = 1  # Publisher role
            current_timestamp = int(time.time())
            privilege_expired_ts = current_timestamp + 3600  # 1 hour from now

            # Generate token
            token = AgoraTokenBuilder.build_token_with_uid(
                settings.AGORA_APP_ID,
                settings.AGORA_APP_CERTIFICATE,
                channel_name,
                uid,
                role,
                privilege_expired_ts
            )

            # Print results
            self.stdout.write(self.style.SUCCESS('Successfully generated token:'))
            self.stdout.write(f'Channel Name: {channel_name}')
            self.stdout.write(f'UID: {uid}')
            self.stdout.write(f'Role: {role}')
            self.stdout.write(f'Expiration: {privilege_expired_ts}')
            self.stdout.write(f'Token: {token}')

            # Verify the token
            is_valid = AgoraTokenBuilder.verify_token(token, settings.AGORA_APP_CERTIFICATE)
            self.stdout.write(f'Token verification: {"Success" if is_valid else "Failed"}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating token: {str(e)}')) 