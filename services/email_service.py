import logging
from typing import List, Optional, Union
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Personalization
import json

logger = logging.getLogger(__name__)

class EmailTemplates:
    """Class containing enterprise-level email templates"""
    
    @staticmethod
    def get_base_template(content: str) -> str:
        """
        Base template with enterprise styling and responsive design
        """
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <title>Alaqa Healthcare</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
                
                /* Reset styles */
                body, p, h1, h2, h3, h4, h5, h6, ul, ol, li {{
                    margin: 0;
                    padding: 0;
                }}
                
                body {{
                    font-family: 'Inter', Arial, sans-serif;
                    line-height: 1.6;
                    background-color: #f4f7fa;
                    color: #2d3748;
                    -webkit-font-smoothing: antialiased;
                }}
                
                /* Container styles */
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }}
                
                /* Header styles */
                .email-header {{
                    background-color: #00796B;
                    padding: 24px;
                    text-align: center;
                }}
                
                .logo {{
                    width: 29px;
                    height: 43px;
                    margin: 0 auto;
                }}
                
                /* Content styles */
                .email-content {{
                    padding: 32px 24px;
                }}
                
                .email-content h1 {{
                    color: #1a202c;
                    font-size: 24px;
                    font-weight: 600;
                    margin-bottom: 16px;
                }}
                
                .email-content p {{
                    margin-bottom: 16px;
                    color: #4a5568;
                }}
                
                /* Button styles */
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #00796B;
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 500;
                    margin: 16px 0;
                }}
                
                /* Data box styles */
                .data-box {{
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 16px;
                    margin: 16px 0;
                }}
                
                .data-box ul {{
                    list-style: none;
                }}
                
                .data-box li {{
                    margin-bottom: 8px;
                    color: #4a5568;
                }}
                
                /* Footer styles */
                .email-footer {{
                    background-color: #f8fafc;
                    padding: 24px;
                    text-align: center;
                    border-top: 1px solid #e2e8f0;
                }}
                
                .footer-links {{
                    margin-bottom: 16px;
                }}
                
                .footer-links a {{
                    color: #00796B;
                    text-decoration: none;
                    margin: 0 8px;
                }}
                
                .footer-text {{
                    color: #718096;
                    font-size: 14px;
                }}
                
                /* Arabic styles */
                .rtl {{
                    direction: rtl;
                    text-align: right;
                }}
                
                /* Responsive styles */
                @media screen and (max-width: 600px) {{
                    .email-container {{
                        width: 100% !important;
                        margin: 0 !important;
                    }}
                    
                    .email-content {{
                        padding: 24px 16px !important;
                    }}
                }}
                
                /* Dark mode support */
                @media (prefers-color-scheme: dark) {{
                    body {{
                        background-color: #1a202c !important;
                    }}
                    
                    .email-container {{
                        background-color: #2d3748 !important;
                    }}
                    
                    .email-content h1 {{
                        color: #f7fafc !important;
                    }}
                    
                    .email-content p {{
                        color: #e2e8f0 !important;
                    }}
                    
                    .data-box {{
                        background-color: #2d3748 !important;
                        border-color: #4a5568 !important;
                    }}
                    
                    .data-box li {{
                        color: #e2e8f0 !important;
                    }}
                    
                    .email-footer {{
                        background-color: #2d3748 !important;
                        border-color: #4a5568 !important;
                    }}
                    
                    .footer-text {{
                        color: #a0aec0 !important;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">
                    <svg class="logo" width="29" height="43" viewBox="0 0 29 43" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M28.2105 28.2382C28.2124 30.5686 27.6369 32.8632 26.5354 34.9168C25.434 36.9705 23.841 38.7192 21.8986 40.0068C19.9562 41.2943 17.7251 42.0806 15.4046 42.2952C13.0841 42.5099 10.7466 42.1463 8.60094 41.2369C6.45532 40.3275 4.56845 38.9007 3.10894 37.084C1.64944 35.2673 0.66284 33.1172 0.237239 30.826C-0.188363 28.5348 -0.0396804 26.1739 0.670032 23.9542C1.37974 21.7345 2.62831 19.7253 4.30422 18.106L8.92158 22.725C7.81881 23.7649 7.05346 25.1118 6.72453 26.5914C6.39561 28.0711 6.51822 29.6154 7.07654 31.0246C7.63487 32.4338 8.60315 33.643 9.85622 34.4959C11.1093 35.3487 12.5895 35.806 14.1052 35.8084C19.014 35.8084 22.9158 30.7092 21.2961 25.966C20.6122 23.9638 19.0471 22.4087 17.5318 20.9314C13.673 17.1703 9.86387 13.3827 6.05642 9.57364L5.65735 9.17285L5.49173 9.00724L0.635907 4.14981C2.71901 2.98129 4.9461 2.09045 7.26043 1.5C11.1275 5.36872 14.9864 9.23082 18.8849 13.0697L19.9017 14.0717C21.9404 16.0789 23.9873 18.0961 25.7213 20.3782C27.4122 22.6157 28.2105 25.4294 28.2105 28.2382Z" fill="url(#paint0_linear_2107_7642)"/>
                        <path d="M13.6855 28.1562H11.1367V30.705H13.6855V28.1562Z" fill="#BC1F38"/>
                        <path d="M17.0741 28.1562H14.5254V30.705H17.0741V28.1562Z" fill="#BC1F38"/>
                        <path d="M13.6855 24.7891H11.1367V27.3379H13.6855V24.7891Z" fill="#BC1F38"/>
                        <path d="M17.0741 24.7891H14.5254V27.3379H17.0741V24.7891Z" fill="#BC1F38"/>
                        <path d="M19.6149 7.97593C21.8174 7.97593 23.6029 6.19045 23.6029 3.98796C23.6029 1.78547 21.8174 0 19.6149 0C17.4124 0 15.627 1.78547 15.627 3.98796C15.627 6.19045 17.4124 7.97593 19.6149 7.97593Z" fill="#BC1F38"/>
                        <defs>
                            <linearGradient id="paint0_linear_2107_7642" x1="20.9914" y1="15.4231" x2="-2.29045" y2="31.3567" gradientUnits="userSpaceOnUse">
                                <stop offset="0.14" stop-color="#602D8B"/>
                                <stop offset="1" stop-color="#BC1F38"/>
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
                <div class="email-content">
                    {content}
                </div>
                <div class="email-footer">
                    <div class="footer-links">
                        <a href="https://doctor.zuwara.net">Doctor Portal</a> |
                        <a href="https://alaqa.net/privacy">Privacy Policy</a> |
                        <a href="https://alaqa.net/terms">Terms of Service</a>
                    </div>
                    <p class="footer-text">
                        © 2024 Alaqa Healthcare. All rights reserved.<br>
                        This is an automated message, please do not reply.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def get_appointment_notification_template(
        doctor_name: str,
        doctor_name_arabic: str,
        slot_time: str,
        duration: int,
        phone_number: str,
        language: str
    ) -> str:
        """
        Enterprise template for appointment notifications
        """
        return f"""
        <!-- English Content -->
        <div class="content-section">
            <h1>New Appointment Scheduled</h1>
            <p>Dear Dr. {doctor_name},</p>
            <p>A new appointment has been scheduled with the following details:</p>
            
            <div class="data-box">
                <ul>
                    <li><strong>📅 Date and Time:</strong> {slot_time}</li>
                    <li><strong>⏱️ Duration:</strong> {duration} minutes</li>
                    <li><strong>📞 Patient Phone:</strong> {phone_number}</li>
                    <li><strong>🗣️ Language:</strong> {language}</li>
                </ul>
            </div>
            
            <a href="https://doctor.zuwara.net/appointments" class="button">View Appointment</a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 32px 0;">
        
        <!-- Arabic Content -->
        <div class="content-section rtl">
            <h1>تم جدولة موعد جديد</h1>
            <p>عزيزي د. {doctor_name_arabic}،</p>
            <p>تم جدولة موعد جديد بالتفاصيل التالية:</p>
            
            <div class="data-box">
                <ul>
                    <li><strong>📅 التاريخ والوقت:</strong> {slot_time}</li>
                    <li><strong>⏱️ المدة:</strong> {duration} دقيقة</li>
                    <li><strong>📞 هاتف المريض:</strong> {phone_number}</li>
                    <li><strong>🗣️ اللغة:</strong> {language}</li>
                </ul>
            </div>
            
            <a href="https://doctor.zuwara.net/appointments" class="button">عرض الموعد</a>
        </div>
        """

    @staticmethod
    def get_verification_template(verification_code: str) -> str:
        """
        Enterprise template for verification emails
        """
        return f"""
        <!-- English Content -->
        <div class="content-section">
            <h1>Verify Your Email</h1>
            <p>Thank you for choosing Alaqa Healthcare. Please use the following verification code to complete your registration:</p>
            
            <div class="data-box" style="text-align: center;">
                <h2 style="font-size: 32px; letter-spacing: 4px; color: #00796B; margin: 8px 0;">
                    {verification_code}
                </h2>
                <p style="font-size: 14px; margin-top: 8px;">This code will expire in 24 hours</p>
            </div>
            
            <div style="margin: 24px 0;">
                <h3 style="font-size: 16px; margin-bottom: 8px;">For your security:</h3>
                <ul style="list-style: none; padding-left: 0;">
                    <li>• Never share this code with anyone</li>
                    <li>• Our team will never ask for this code</li>
                    <li>• Only enter this code on the official Alaqa website</li>
                </ul>
            </div>
        </div>
        
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 32px 0;">
        
        <!-- Arabic Content -->
        <div class="content-section rtl">
            <h1>تحقق من بريدك الإلكتروني</h1>
            <p>شكراً لاختيارك علاقة للرعاية الصحية. يرجى استخدام رمز التحقق التالي لإكمال تسجيلك:</p>
            
            <div class="data-box" style="text-align: center;">
                <h2 style="font-size: 32px; letter-spacing: 4px; color: #00796B; margin: 8px 0;">
                    {verification_code}
                </h2>
                <p style="font-size: 14px; margin-top: 8px;">سينتهي هذا الرمز خلال 24 ساعة</p>
            </div>
            
            <div style="margin: 24px 0;">
                <h3 style="font-size: 16px; margin-bottom: 8px;">لحماية أمان حسابك:</h3>
                <ul style="list-style: none; padding-right: 0;">
                    <li>• لا تشارك هذا الرمز مع أي شخص</li>
                    <li>• لن يطلب فريقنا هذا الرمز أبداً</li>
                    <li>• أدخل هذا الرمز فقط على الموقع الرسمي لعلاقة</li>
                </ul>
            </div>
        </div>
        """

class EmailService:
    """Service for sending emails using SendGrid with enterprise-level templates"""
    
    def __init__(self):
        """Initialize SendGrid client with API key"""
        self.api_key = settings.SENDGRID_API_KEY
        self.default_from_email = settings.DEFAULT_FROM_EMAIL
        logger.info(f"Initializing SendGrid client with API key ending in: ...{self.api_key[-4:]}")
        logger.info(f"Default from email: {self.default_from_email}")
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
        Send an email using SendGrid with enterprise templates
        """
        try:
            # Convert single email to list
            if isinstance(to_emails, str):
                to_emails = [to_emails]
                
            logger.info(f"Preparing to send email to: {to_emails}")
            logger.info(f"Subject: {subject}")
            logger.info(f"From email: {from_email or self.default_from_email}")
            
            # Create mail object with base template
            mail = Mail(
                from_email=from_email or self.default_from_email,
                subject=subject,
                to_emails=to_emails,
                html_content=EmailTemplates.get_base_template(html_content)
            )
            
            # Add reply-to if provided
            if reply_to:
                mail.reply_to = Email(reply_to)
                logger.info(f"Added reply-to: {reply_to}")
            
            # Log the full mail object for debugging
            logger.debug(f"Mail object: {mail.get()}")
            
            # Send email
            response = self.client.send(mail)
            
            # Log detailed response
            logger.info(f"SendGrid Response Status Code: {response.status_code}")
            logger.info(f"SendGrid Response Headers: {json.dumps(dict(response.headers), indent=2)}")
            logger.info(f"SendGrid Response Body: {response.body.decode() if response.body else 'No body'}")
            
            if response.status_code >= 400:
                logger.error(f"SendGrid API Error - Status: {response.status_code}")
                logger.error(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
                logger.error(f"Response Body: {response.body.decode() if response.body else 'No body'}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'message': f"Failed to send email: {response.body.decode() if response.body else 'Unknown error'}"
                }
            
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
            logger.error(f"Failed to send email to {to_emails}. Error: {str(e)}", exc_info=True)
            if hasattr(e, 'body'):
                logger.error(f"SendGrid Error Body: {e.body.decode() if e.body else 'No body'}")
            if hasattr(e, 'headers'):
                logger.error(f"SendGrid Error Headers: {json.dumps(dict(e.headers), indent=2)}")
            return {
                'success': False,
                'message': f"Failed to send email: {str(e)}"
            }

    def send_verification_email(self, to_email: str, verification_code: str) -> dict:
        """
        Send a verification email with enterprise template
        """
        subject = "Verify Your Email - Alaqa Healthcare"
        html_content = EmailTemplates.get_verification_template(verification_code)
        
        return self.send_email(
            to_email,
            subject,
            html_content
        )

    def send_appointment_notification(
        self,
        to_email: str,
        doctor_name: str,
        doctor_name_arabic: str,
        slot_time: str,
        duration: int,
        phone_number: str,
        language: str
    ) -> dict:
        """
        Send an appointment notification with enterprise template
        """
        subject = "New Appointment Scheduled - علاقة: موعد جديد"
        html_content = EmailTemplates.get_appointment_notification_template(
            doctor_name=doctor_name,
            doctor_name_arabic=doctor_name_arabic,
            slot_time=slot_time,
            duration=duration,
            phone_number=phone_number,
            language=language
        )
        
        return self.send_email(
            to_email,
            subject,
            html_content
        )

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