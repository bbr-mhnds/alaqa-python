from django.test import TestCase
from django.conf import settings
from .services import OTPService
from .models import OTP

class OTPServiceTests(TestCase):
    def setUp(self):
        """Set up test environment"""
        # Store original DEBUG setting
        self.original_debug = settings.DEBUG
        # Set DEBUG to False to test actual SMS sending
        settings.DEBUG = False
        
    def tearDown(self):
        """Clean up test environment"""
        # Restore original DEBUG setting
        settings.DEBUG = self.original_debug

    def test_send_arabic_sms(self):
        """Test sending Arabic SMS message"""
        # Test phone number
        phone_number = "555552022"
        
        # Arabic test message (under 100 characters)
        message = "مرحباً بك في تطبيق زوارة! رمز التحقق الخاص بك هو"
        
        # Create OTP service instance
        otp_service = OTPService()
        
        # First validate the phone number
        validated_number, validation_message = otp_service.validate_phone_number(phone_number)
        self.assertIsNotNone(validated_number, "Phone number validation failed")
        
        # Test SMS sending
        success, response = otp_service.send_sms(validated_number, message)
        
        # Log the response for debugging
        print(f"SMS Send Response: {response}")
        
        # Assertions
        self.assertTrue(success, f"SMS sending failed: {response}")
        self.assertIn("successfully", response.lower())

    def test_create_and_send_otp(self):
        """Test complete OTP creation and sending flow"""
        phone_number = "555552022"
        
        # Test the complete flow
        result = OTPService.create_and_send_otp(phone_number)
        
        # Log the result for debugging
        print(f"OTP Creation Result: {result}")
        
        # Assertions
        self.assertTrue(result['success'], f"OTP creation failed: {result['message']}")
        self.assertIsNotNone(result['otp_id'], "OTP ID should not be None")
        
        # Verify OTP was created in database
        otp = OTP.objects.get(id=result['otp_id'])
        self.assertEqual(otp.phone_number, "966555552022")  # Should be converted to full format
        self.assertFalse(otp.is_verified)
        self.assertEqual(otp.attempts, 0)
