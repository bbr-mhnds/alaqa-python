import os
import django
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.email_service import EmailService

def generate_otp():
    """Generate a 6-digit OTP code"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def test_send_otp_email():
    # Create email service instance
    email_service = EmailService()
    
    # Generate OTP
    otp_code = generate_otp()
    
    # List of recipients
    recipients = ["babar@alaqa.net", "abdulrahman@alaqa.net"]
    
    # Send email to each recipient
    for recipient in recipients:
        result = email_service.send_otp_email(
            to_email=recipient,
            otp_code=otp_code
        )
        
        # Print result for each recipient
        print(f"\nEmail sending result for {recipient}:")
        print(f"Status: {result}")
        print(f"OTP code sent: {otp_code}")

if __name__ == "__main__":
    test_send_otp_email() 