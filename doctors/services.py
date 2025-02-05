import logging
from django.core.mail import send_mail
from django.conf import settings
from otp.services import OTPService

logger = logging.getLogger(__name__)

class DoctorVerificationService:
    @staticmethod
    def send_verification_codes(email, phone, registration_data=None):
        """Send verification codes via SMS only"""
        try:
            # Create and send OTP using OTPService
            otp_result = OTPService.create_and_send_otp(phone)
            
            if not otp_result['success']:
                return {
                    'success': False,
                    'message': otp_result['message'],
                    'verification_id': None
                }
            
            # Create DoctorVerification instance
            from django.utils import timezone
            from .models import DoctorVerification

            try:
                # Extract file fields from registration data
                license_document = registration_data.pop('license_document', None) if registration_data else None
                qualification_document = registration_data.pop('qualification_document', None) if registration_data else None
                additional_documents = registration_data.pop('additional_documents', None) if registration_data else None
                
                # Store file paths in registration data
                if license_document:
                    registration_data['license_document_path'] = f'doctors/licenses/{license_document.name}'
                if qualification_document:
                    registration_data['qualification_document_path'] = f'doctors/qualifications/{qualification_document.name}'
                if additional_documents:
                    registration_data['additional_documents_path'] = f'doctors/additional/{additional_documents.name}'
                
                # Create verification instance
                verification = DoctorVerification.objects.create(
                    email=email,
                    phone=phone,
                    email_verified=True,  # Auto verify email
                    phone_verified=False,  # Will be verified with SMS code
                    registration_data=registration_data or {},
                    expires_at=timezone.now() + timezone.timedelta(minutes=10)
                )

                # Handle file uploads
                if license_document:
                    verification.license_document.save(
                        license_document.name,
                        license_document,
                        save=False
                    )
                if qualification_document:
                    verification.qualification_document.save(
                        qualification_document.name,
                        qualification_document,
                        save=False
                    )
                
                verification.save()
                logger.info(f"[DOCTOR_DEBUG] Created verification instance for {email}")
                    
                return {
                    'success': True,
                    'message': 'Verification codes sent successfully',
                    'verification_id': str(verification.id),
                    'otp_id': otp_result['otp_id']
                }
                    
            except Exception as e:
                logger.error(f"[DOCTOR_DEBUG] Failed to create verification instance: {str(e)}")
                return {
                    'success': False,
                    'message': f"Failed to create verification instance: {str(e)}",
                    'verification_id': None
                }
                
        except Exception as e:
            logger.error(f"[DOCTOR_DEBUG] Error in send_verification_codes: {str(e)}")
            return {
                'success': False,
                'message': f"Error sending verification codes: {str(e)}",
                'verification_id': None
            }