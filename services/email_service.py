import logging
from typing import List, Optional, Union
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Personalization

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails using SendGrid"""
    
    def __init__(self):
        """Initialize SendGrid client with API key"""
        self.api_key = settings.SENDGRID_API_KEY
        self.default_from_email = settings.DEFAULT_FROM_EMAIL
        self.client = SendGridAPIClient(self.api_key)

    def send_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> dict:
        """
        Send an email using SendGrid
        
        Args:
            to_emails: Single email string or list of email addresses
            subject: Email subject
            html_content: HTML content of the email
            from_email: Optional sender email (defaults to settings.DEFAULT_FROM_EMAIL)
            reply_to: Optional reply-to email address
            
        Returns:
            dict: Response from SendGrid API
        """
        try:
            # Convert single email to list
            if isinstance(to_emails, str):
                to_emails = [to_emails]
                
            # Create mail object
            mail = Mail(
                from_email=from_email or self.default_from_email,
                subject=subject,
                to_emails=to_emails,
                html_content=html_content
            )
            
            # Add reply-to if provided
            if reply_to:
                mail.reply_to = Email(reply_to)
            
            # Send email
            response = self.client.send(mail)
            
            logger.info(
                f"Email sent successfully to {to_emails}. "
                f"Status code: {response.status_code}"
            )
            
            return {
                'success': True,
                'status_code': response.status_code,
                'message': 'Email sent successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_emails}. Error: {str(e)}")
            return {
                'success': False,
                'message': f"Failed to send email: {str(e)}"
            }
    
    def send_template_email(
        self,
        to_emails: Union[str, List[str]],
        template_id: str,
        dynamic_data: dict,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> dict:
        """
        Send a templated email using SendGrid templates
        
        Args:
            to_emails: Single email string or list of email addresses
            template_id: SendGrid template ID
            dynamic_data: Dictionary of dynamic template data
            from_email: Optional sender email (defaults to settings.DEFAULT_FROM_EMAIL)
            reply_to: Optional reply-to email address
            
        Returns:
            dict: Response from SendGrid API
        """
        try:
            # Convert single email to list
            if isinstance(to_emails, str):
                to_emails = [to_emails]
            
            # Create mail object
            mail = Mail(from_email=from_email or self.default_from_email)
            
            # Add personalization for each recipient
            for email in to_emails:
                personalization = Personalization()
                personalization.add_to(To(email))
                personalization.dynamic_template_data = dynamic_data
                mail.add_personalization(personalization)
            
            # Set template ID
            mail.template_id = template_id
            
            # Add reply-to if provided
            if reply_to:
                mail.reply_to = Email(reply_to)
            
            # Send email
            response = self.client.send(mail)
            
            logger.info(
                f"Template email sent successfully to {to_emails}. "
                f"Status code: {response.status_code}"
            )
            
            return {
                'success': True,
                'status_code': response.status_code,
                'message': 'Email sent successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to send template email to {to_emails}. Error: {str(e)}")
            return {
                'success': False,
                'message': f"Failed to send email: {str(e)}"
            }

    def send_verification_email(self, to_email: str, verification_code: str) -> dict:
        """
        Send a verification email with a verification code
        
        Args:
            to_email: Recipient email address
            verification_code: The verification code to send
            
        Returns:
            dict: Response from SendGrid API
        """
        subject = "Verify Your Email - Alaqa"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Email Verification</h2>
            <p>Thank you for registering with Alaqa. Please use the following code to verify your email address:</p>
            <div style="background-color: #f5f5f5; padding: 15px; text-align: center; margin: 20px 0;">
                <h1 style="color: #4a90e2; margin: 0; font-size: 32px;">{verification_code}</h1>
            </div>
            <p>This code will expire in 24 hours.</p>
            <p>If you didn't request this verification, please ignore this email.</p>
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="color: #666; font-size: 12px;">This is an automated message, please do not reply.</p>
        </div>
        """
        
        return self.send_email(
            to_email,
            subject,
            html_content
        )

    def send_password_reset_email(self, to_email: str, reset_code: str) -> dict:
        """
        Send a password reset email with a reset code
        
        Args:
            to_email: Recipient email address
            reset_code: The password reset code
            
        Returns:
            dict: Response from SendGrid API
        """
        subject = "Reset Your Password - Alaqa"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Password Reset Request</h2>
            <p>We received a request to reset your password. Use the following code to reset your password:</p>
            <div style="background-color: #f5f5f5; padding: 15px; text-align: center; margin: 20px 0;">
                <h1 style="color: #4a90e2; margin: 0; font-size: 32px;">{reset_code}</h1>
            </div>
            <p>This code will expire in 24 hours.</p>
            <p>If you didn't request a password reset, please ignore this email.</p>
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="color: #666; font-size: 12px;">This is an automated message, please do not reply.</p>
        </div>
        """
        
        return self.send_email(
            to_email,
            subject,
            html_content
        )

    def send_otp_email(self, to_email: str, otp_code: str) -> dict:
        """
        Send an OTP email with a professional bilingual template
        
        Args:
            to_email: Recipient email address
            otp_code: The OTP code to send
            
        Returns:
            dict: Response from SendGrid API
        """
        subject = "Your Verification Code - رمز التحقق الخاص بك"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Vibrawy:wght@400;700&display=swap" rel="stylesheet">
            <style>
                @font-face {{
                    font-family: 'Vibrawy';
                    src: url('https://fonts.googleapis.com/css2?family=Vibrawy:wght@400;700&display=swap');
                }}
                .arabic {{
                    font-family: 'Vibrawy', Arial, sans-serif;
                    direction: rtl;
                    text-align: right;
                    line-height: 1.6;
                }}
            </style>
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; margin-top: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <!-- Header -->
                <tr>
                    <td style="background-color: #00796B; padding: 30px 40px; text-align: center;">
                        <img src="https://alaqa.net/logo.png" alt="Alaqa Healthcare" style="max-width: 150px; height: auto;" />
                    </td>
                </tr>
                
                <!-- Content -->
                <tr>
                    <td style="padding: 40px;">
                        <!-- Arabic Content -->
                        <div class="arabic" style="margin-bottom: 30px;">
                            <h1 style="color: #333333; font-size: 24px; margin: 0 0 20px 0;">تحقق من حسابك</h1>
                            <p style="color: #666666; font-size: 16px; margin: 0 0 20px 0;">
                                شكراً لاختيارك علاقة للرعاية الصحية. للتحقق من أمان حسابك، يرجى استخدام رمز التحقق التالي:
                            </p>
                        </div>
                        
                        <!-- English Content -->
                        <h1 style="color: #333333; font-size: 24px; margin: 0 0 20px 0;">Verify Your Account</h1>
                        <p style="color: #666666; font-size: 16px; line-height: 24px; margin: 0 0 20px 0;">
                            Thank you for choosing Alaqa Healthcare. To ensure the security of your account, please use the following verification code:
                        </p>
                        
                        <!-- OTP Code Box -->
                        <div style="background-color: #f8f9fa; border: 2px solid #e9ecef; border-radius: 8px; padding: 20px; margin: 30px 0; text-align: center;">
                            <span style="font-family: 'Courier New', monospace; font-size: 32px; font-weight: bold; color: #00796B; letter-spacing: 4px;">
                                {otp_code}
                            </span>
                        </div>
                        
                        <!-- Arabic Security Notes -->
                        <div class="arabic" style="margin-bottom: 20px;">
                            <p style="color: #666666; font-size: 16px; margin: 0 0 20px 0;">
                                سينتهي هذا الرمز خلال <strong>24 ساعة</strong>. إذا لم تطلب رمز التحقق هذا، يرجى تجاهل هذا البريد الإلكتروني.
                            </p>
                            <p style="color: #666666; font-size: 16px; margin: 0 0 10px 0;">
                                لحماية أمان حسابك:
                            </p>
                            <ul style="color: #666666; font-size: 16px; margin: 0 0 20px 0;">
                                <li>لا تشارك هذا الرمز مع أي شخص</li>
                                <li>لن يطلب فريقنا هذا الرمز أبداً</li>
                                <li>أدخل هذا الرمز فقط على الموقع الرسمي لعلاقة</li>
                            </ul>
                        </div>
                        
                        <!-- English Security Notes -->
                        <p style="color: #666666; font-size: 16px; line-height: 24px; margin: 0 0 20px 0;">
                            This code will expire in <strong>24 hours</strong>. If you didn't request this verification code, please ignore this email.
                        </p>
                        <p style="color: #666666; font-size: 16px; line-height: 24px; margin: 0 0 20px 0;">
                            For your security:
                        </p>
                        <ul style="color: #666666; font-size: 16px; line-height: 24px; margin: 0 0 20px 0;">
                            <li>Never share this code with anyone</li>
                            <li>Our team will never ask for this code</li>
                            <li>Only enter this code on the official Alaqa website</li>
                        </ul>
                    </td>
                </tr>
                
                <!-- Footer -->
                <tr>
                    <td style="background-color: #f8f9fa; padding: 30px 40px; border-top: 1px solid #e9ecef;">
                        <!-- Arabic Footer -->
                        <div class="arabic" style="margin-bottom: 20px;">
                            <p style="color: #999999; font-size: 14px; line-height: 20px; margin: 0; text-align: center;">
                                هذه رسالة آلية، يرجى عدم الرد عليها.<br>
                                إذا كنت بحاجة إلى مساعدة، يرجى التواصل مع فريق الدعم على support@alaqa.net
                            </p>
                        </div>
                        
                        <!-- English Footer -->
                        <p style="color: #999999; font-size: 14px; line-height: 20px; margin: 0; text-align: center;">
                            This is an automated message, please do not reply.<br>
                            If you need assistance, please contact our support team at support@alaqa.net
                        </p>
                        
                        <!-- Links -->
                        <div style="text-align: center; margin-top: 20px;">
                            <a href="https://alaqa.net" style="color: #00796B; text-decoration: none; margin: 0 10px;">الموقع | Website</a> |
                            <a href="https://alaqa.net/privacy" style="color: #00796B; text-decoration: none; margin: 0 10px;">سياسة الخصوصية | Privacy Policy</a> |
                            <a href="https://alaqa.net/terms" style="color: #00796B; text-decoration: none; margin: 0 10px;">الشروط والأحكام | Terms of Service</a>
                        </div>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email,
            subject,
            html_content
        ) 