import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from otp.services import OTPService

def test_doctor_verification():
    """Test sending verification code via SMS"""
    
    # Test data
    phone_number = "555552022"  # Test phone number
    email = "babar@alaqa.net"   # Test email (needed for record keeping)
    
    # Send verification
    result = OTPService.create_and_send_doctor_verification(phone_number, email)
    
    # Print results
    print("\nDoctor Verification Results:")
    print("-" * 50)
    print(f"Overall Status: {'Success' if result['success'] else 'Failed'}")
    print(f"Message: {result['message']}")
    print(f"OTP ID: {result['otp_id']}")
    print("\nSMS Status:")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")

if __name__ == "__main__":
    test_doctor_verification() 