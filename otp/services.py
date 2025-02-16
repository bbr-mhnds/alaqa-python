import random
import requests
import logging
from django.conf import settings
from .models import OTP
from django.utils import timezone
from services.email_service import EmailService

logger = logging.getLogger(__name__)

class OTPService:
    """
    Service class for handling OTP operations
    """
    def __init__(self):
        """Initialize services"""
        self.email_service = EmailService()

    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP code"""
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        logger.info(f"[OTP_DEBUG] Generated OTP code: {otp_code}")
        return otp_code

    @staticmethod
    def get_otp_by_id(otp_id):
        """Get OTP instance by ID"""
        try:
            return OTP.objects.get(id=otp_id)
        except OTP.DoesNotExist:
            logger.error(f"[OTP_DEBUG] OTP not found with ID: {otp_id}")
            return None
        except Exception as e:
            logger.exception(f"[OTP_DEBUG] Error retrieving OTP with ID {otp_id}")
            return None

    @staticmethod
    def validate_phone_number(phone_number):
        """Validate and format phone number"""
        # Remove any spaces or special characters
        phone_number = ''.join(filter(str.isdigit, phone_number))
        
        # Validate Saudi phone number format
        if phone_number.startswith('966'):
            if len(phone_number) != 12:  # 966 + 9 digits
                return None, "Invalid Saudi phone number length"
        elif phone_number.startswith('05'):
            phone_number = '966' + phone_number[1:]  # Convert 05x to 966x
        elif phone_number.startswith('5'):
            phone_number = '966' + phone_number
        else:
            return None, "Invalid phone number format"
            
        return phone_number, "Valid phone number"

    @staticmethod
    def send_sms(phone_number, message):
        """Send SMS using Dreams API"""
        logger.info(f"[OTP_DEBUG] Attempting to send SMS to {phone_number}")
        logger.info(f"[OTP_DEBUG] Message content: {message}")
        
        # In debug mode, just log the message and return success
        if settings.DEBUG:
            logger.info(f"[OTP_DEBUG] Debug mode: Simulating SMS send to {phone_number}")
            logger.info(f"[OTP_DEBUG] Debug mode: Message would be: {message}")
            return True, "SMS simulated successfully (Debug Mode)"
        
        # Format phone number: remove country code and leading zeros
        if phone_number.startswith('966'):
            phone_number = phone_number[3:]  # Remove 966
        phone_number = phone_number.lstrip('0')  # Remove any leading zeros
        logger.info(f"[OTP_DEBUG] Formatted number for sending: {phone_number}")
        
        # Validate required settings
        required_settings = [
            'DREAMS_SMS_API_URL',
            'DREAMS_SMS_USER',
            'DREAMS_SMS_SECRET_KEY',
            'DREAMS_SMS_SENDER'
        ]
        
        for setting in required_settings:
            if not hasattr(settings, setting) or not getattr(settings, setting):
                logger.error(f"[OTP_DEBUG] Missing required setting: {setting}")
                return False, f"SMS configuration error: Missing {setting}"
            
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
            response_codes = {
                '-124': "Invalid credentials or IP not whitelisted",
                '-120': "Invalid sender ID",
                '-110': "Invalid phone number format",
                '-111': "Insufficient credit",
                '1': "Success"
            }
            
            if cleaned_response in response_codes:
                is_success = cleaned_response == '1'
                message = response_codes[cleaned_response]
                log_method = logger.info if is_success else logger.error
                log_method(f"[OTP_DEBUG] SMS API Response: {message}")
                return is_success, message
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
            # Validate phone number
            validated_number, validation_message = cls.validate_phone_number(phone_number)
            if not validated_number:
                logger.error(f"[OTP_DEBUG] Invalid phone number: {validation_message}")
                return {
                    'success': False,
                    'message': validation_message,
                    'otp_id': None
                }
                
            # Check for existing unverified OTP
            existing_otp = OTP.objects.filter(
                phone_number=validated_number,
                is_verified=False,
                expires_at__gt=timezone.now()
            ).first()
            
            if existing_otp and existing_otp.is_valid:
                logger.info(f"[OTP_DEBUG] Valid OTP already exists for {validated_number}")
                message = f"""ZUWARA: Your verification code is {existing_otp.otp_code}"""
                success, response = cls.send_sms(validated_number, message)
                return {
                    'success': success,
                    'message': response,
                    'otp_id': str(existing_otp.id) if success else None
                }
            
            # Generate new OTP
            otp_code = cls.generate_otp()
            logger.info(f"[OTP_DEBUG] Generated OTP code: {otp_code} for phone: {validated_number}")
            
            # Create OTP record with proper expiration time
            otp = OTP.objects.create(
                phone_number=validated_number,
                otp_code=otp_code,
                expires_at=timezone.now() + timezone.timedelta(days=1)  # Set expiration to 1 day
            )
            logger.info(f"[OTP_DEBUG] Created OTP record - ID: {otp.id}, Phone: {validated_number}")
            
            # Prepare message
            message = f"""ZUWARA: Your verification code is {otp_code}"""
            logger.info(f"[OTP_DEBUG] Prepared SMS message: {message}")
            
            # Send SMS
            success, response = cls.send_sms(validated_number, message)
            logger.info(f"[OTP_DEBUG] SMS send result - Success: {success}, Response: {response}")
            
            if not success:
                logger.error(f"[OTP_DEBUG] Failed to send SMS - OTP ID: {otp.id}, Phone: {validated_number}")
            
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

    @classmethod
    def create_and_send_doctor_verification(cls, phone_number, email):
        """
        Create and send OTP via SMS for doctor verification
        
        Args:
            phone_number: Doctor's phone number
            email: Doctor's email address (kept for compatibility)
            
        Returns:
            dict: Response containing success status and message
        """
        logger.info(f"[OTP_DEBUG] Starting doctor verification for phone: {phone_number}")
        
        try:
            # Create and send OTP
            otp_result = cls.create_and_send_otp(phone_number)
            
            if not otp_result['success']:
                logger.error(f"[OTP_DEBUG] Failed to send OTP: {otp_result['message']}")
                return otp_result
            
            logger.info(f"[OTP_DEBUG] Doctor verification successful")
            return otp_result
            
        except Exception as e:
            logger.exception("[OTP_DEBUG] Error in create_and_send_doctor_verification")
            return {
                'success': False,
                'message': f"Failed to send verification: {str(e)}",
                'otp_id': None
            } 