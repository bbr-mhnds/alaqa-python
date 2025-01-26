import random
import requests
import logging
from django.conf import settings
from .models import OTP

logger = logging.getLogger(__name__)

class OTPService:
    """
    Service class for handling OTP operations
    """
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP code"""
        otp_code = "000000"  # Fixed OTP for testing
        logger.info(f"[OTP_DEBUG] Generated OTP code: {otp_code}")
        return otp_code

    @staticmethod
    def send_sms(phone_number, message):
        """Send SMS using Dreams API"""
        logger.info(f"[OTP_DEBUG] Attempting to send SMS to {phone_number}")
        logger.info(f"[OTP_DEBUG] Message content: {message}")
        
        # Format phone number: remove country code and leading zeros
        if phone_number.startswith('966'):
            phone_number = phone_number[3:]  # Remove 966
        phone_number = phone_number.lstrip('0')  # Remove any leading zeros
        logger.info(f"[OTP_DEBUG] Formatted number for sending: {phone_number}")
        
        # Development mode - always succeed and log the OTP
        if settings.DEBUG:
            logger.info(f"[OTP_DEBUG] DEV MODE - SMS would be sent to {phone_number}")
            logger.info(f"[OTP_DEBUG] DEV MODE - Message content: {message}")
            return True, "SMS sent successfully (Development Mode)"
            
        url = settings.DREAMS_SMS_API_URL
        params = {
            'user': settings.DREAMS_SMS_USER,
            'secret_key': settings.DREAMS_SMS_SECRET_KEY,
            'to': phone_number,
            'message': message,
            'sender': settings.DREAMS_SMS_SENDER
        }
        
        try:
            logger.info(f"[OTP_DEBUG] Sending SMS with params: {params}")
            logger.info(f"[OTP_DEBUG] API URL: {url}")
            
            response = requests.get(url, params=params, timeout=10)
            response_text = response.text.strip()
            
            logger.info(f"[OTP_DEBUG] SMS API Raw Response: {response_text}")
            logger.info(f"[OTP_DEBUG] SMS API Response Status Code: {response.status_code}")
            
            # Clean response text - remove any non-numeric characters except minus sign
            cleaned_response = ''.join(c for c in response_text if c.isdigit() or c == '-')
            
            # Handle different response codes
            if cleaned_response == '-124':
                logger.error("[OTP_DEBUG] SMS API Error: Invalid credentials")
                return False, "Failed to send SMS: Invalid credentials or IP not whitelisted"
            elif cleaned_response == '-120':
                logger.error("[OTP_DEBUG] SMS API Error: Invalid sender ID")
                return False, "Failed to send SMS: Invalid sender ID"
            elif cleaned_response == '-110':
                logger.error("[OTP_DEBUG] SMS API Error: Invalid phone number format")
                return False, "Failed to send SMS: Invalid phone number format"
            elif cleaned_response == '-111':
                logger.error("[OTP_DEBUG] SMS API Error: Insufficient credit")
                return False, "Failed to send SMS: Insufficient credit"
            elif cleaned_response == '1':
                logger.info("[OTP_DEBUG] SMS sent successfully")
                return True, "SMS sent successfully"
            elif cleaned_response.startswith('-'):
                logger.error(f"[OTP_DEBUG] SMS API Error Code: {cleaned_response}")
                return False, f"Failed to send SMS: API error {cleaned_response}"
            else:
                logger.info(f"[OTP_DEBUG] SMS sent with response: {cleaned_response}")
                return True, "SMS sent successfully"
            
        except requests.Timeout:
            logger.error("[OTP_DEBUG] SMS API request timed out")
            return False, "Failed to send SMS: Request timed out"
        except requests.RequestException as e:
            logger.error(f"[OTP_DEBUG] SMS API request failed: {str(e)}")
            return False, f"Failed to send SMS: {str(e)}"

    @classmethod
    def create_and_send_otp(cls, phone_number):
        """Create and send OTP to the given phone number"""
        logger.info(f"[OTP_DEBUG] Starting OTP creation for phone: {phone_number}")
        
        try:
            # Generate OTP
            otp_code = cls.generate_otp()
            logger.info(f"[OTP_DEBUG] Generated OTP code: {otp_code} for phone: {phone_number}")
            
            # Create OTP record
            otp = OTP.objects.create(
                phone_number=phone_number,
                otp_code=otp_code
            )
            logger.info(f"[OTP_DEBUG] Created OTP record - ID: {otp.id}, Phone: {phone_number}, Code: {otp_code}")
            
            # Prepare message
            message = f"""ZUWARA: Your verification code is {otp_code}"""
            logger.info(f"[OTP_DEBUG] Prepared SMS message: {message}")
            
            # Send SMS
            success, response = cls.send_sms(phone_number, message)
            logger.info(f"[OTP_DEBUG] SMS send result - Success: {success}, Response: {response}")
            
            if not success:
                logger.error(f"[OTP_DEBUG] Failed to send SMS - OTP ID: {otp.id}, Phone: {phone_number}")
            
            result = {
                'success': success,
                'message': response,
                'otp_id': str(otp.id) if success else None
            }
            logger.info(f"[OTP_DEBUG] Final result: {result}")
            return result
            
        except Exception as e:
            logger.exception("[OTP_DEBUG] Error in create_and_send_otp")
            return {
                'success': False,
                'message': f"Failed to create OTP: {str(e)}",
                'otp_id': None
            }

    @classmethod
    def verify_otp(cls, phone_number, otp_code):
        """Verify the OTP code"""
        try:
            logger.info(f"Verifying OTP for {phone_number}")
            otp = OTP.objects.filter(
                phone_number=phone_number,
                otp_code=otp_code,
                is_verified=False
            ).latest('created_at')
            
            if not otp.is_valid:
                if otp.is_expired:
                    logger.info(f"OTP expired for {phone_number}")
                    return False, "OTP has expired"
                if otp.attempts >= 3:
                    logger.info(f"Maximum attempts exceeded for {phone_number}")
                    return False, "Maximum verification attempts exceeded"
                logger.info(f"Invalid OTP for {phone_number}")
                return False, "Invalid OTP"
            
            # Increment attempts
            otp.attempts += 1
            
            if otp_code == otp.otp_code:
                otp.is_verified = True
                otp.save()
                logger.info(f"OTP verified successfully for {phone_number}")
                return True, "OTP verified successfully"
            
            otp.save()
            logger.info(f"Invalid OTP code for {phone_number}")
            return False, "Invalid OTP code"
            
        except OTP.DoesNotExist:
            logger.info(f"No valid OTP found for {phone_number}")
            return False, "Invalid OTP"
        except Exception as e:
            logger.exception("Error in verify_otp")
            return False, f"Error verifying OTP: {str(e)}" 