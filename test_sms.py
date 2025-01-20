import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Force DEBUG to False for real API testing
settings.DEBUG = False

from otp.services import OTPService

# Test phone number
phone_number = "555552022"

# Create and send OTP
result = OTPService.create_and_send_otp(phone_number)
print("Result:", result) 