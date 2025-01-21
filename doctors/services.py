import logging
from django.core.mail import send_mail
from django.conf import settings
from otp.services import OTPService

logger = logging.getLogger(__name__)

class DoctorVerificationService:
    @staticmethod
    def send_email_verification(email, code):
        """Send verification email to doctor"""
        try:
            subject = "ZUWARA - Email Verification"
            message = f"""
            Thank you for registering with ZUWARA.
            
            Your email verification code is: {code}
            
            Please use this code to complete your registration.
            Do not share this code with anyone.
            
            Best regards,
            ZUWARA Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            logger.info(f"[DOCTOR_DEBUG] Verification email sent to {email}")
            return True, "Verification email sent successfully"
            
        except Exception as e:
            logger.error(f"[DOCTOR_DEBUG] Failed to send verification email: {str(e)}")
            return False, f"Failed to send verification email: {str(e)}"

    @staticmethod
    def generate_verification_codes():
        """Generate unique codes for email and SMS verification"""
        email_code = OTPService.generate_otp()
        sms_code = OTPService.generate_otp()
        
        # Ensure codes are different
        while email_code == sms_code:
            sms_code = OTPService.generate_otp()
            
        return email_code, sms_code

    @staticmethod
    def send_verification_codes(email, phone):
        """Send verification codes via email and SMS"""
        email_code, sms_code = DoctorVerificationService.generate_verification_codes()
        
        # Send email verification
        email_success, email_message = DoctorVerificationService.send_email_verification(
            email, email_code
        )
        
        # Send SMS verification
        sms_success, sms_message = OTPService.send_sms(
            phone,
            f"ZUWARA: Your phone verification code is: {sms_code}. Do not share this code with anyone."
        )
        
        return {
            'email': {
                'success': email_success,
                'message': email_message,
                'code': email_code
            },
            'sms': {
                'success': sms_success,
                'message': sms_message,
                'code': sms_code
            }
        } 