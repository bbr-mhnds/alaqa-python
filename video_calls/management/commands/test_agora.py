from django.core.management.base import BaseCommand
from integrations.services.agora import AgoraService

class Command(BaseCommand):
    help = 'Test Agora token generation'

    def add_arguments(self, parser):
        parser.add_argument('channel_name', type=str, help='Channel name for the token')
        parser.add_argument('--uid', type=int, default=0, help='User ID')
        parser.add_argument('--role', type=int, default=1, help='User role (1=publisher, 2=subscriber)')

    def handle(self, *args, **options):
        try:
            agora_service = AgoraService()
            token = agora_service.generate_rtc_token(
                channel_name=options['channel_name'],
                uid=options['uid'],
                role=options['role']
            )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully generated token:'))
            self.stdout.write(f'Channel: {options["channel_name"]}')
            self.stdout.write(f'UID: {options["uid"]}')
            self.stdout.write(f'Role: {options["role"]}')
            self.stdout.write(f'Token: {token}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating token: {str(e)}')) 