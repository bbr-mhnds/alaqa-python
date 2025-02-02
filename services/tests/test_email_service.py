from django.test import TestCase
from django.conf import settings
from unittest.mock import patch, MagicMock
from ..email_service import EmailService

class EmailServiceTests(TestCase):
    def setUp(self):
        self.email_service = EmailService()
        self.test_email = "test@example.com"
        
    @patch('services.email_service.SendGridAPIClient')
    def test_send_email(self, mock_sendgrid):
        # Mock the SendGrid client response
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_sendgrid.return_value.send.return_value = mock_response
        
        # Test sending a single email
        result = self.email_service.send_email(
            to_emails=self.test_email,
            subject="Test Email",
            html_content="<p>Test content</p>"
        )
        
        # Assert the email was sent successfully
        self.assertTrue(result['success'])
        self.assertEqual(result['status_code'], 202)
        
        # Verify SendGrid was called with correct parameters
        mock_sendgrid.return_value.send.assert_called_once()
        
    @patch('services.email_service.SendGridAPIClient')
    def test_send_template_email(self, mock_sendgrid):
        # Mock the SendGrid client response
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_sendgrid.return_value.send.return_value = mock_response
        
        # Test data
        template_id = "d-template123"
        dynamic_data = {"name": "Test User", "code": "123456"}
        
        # Test sending a template email
        result = self.email_service.send_template_email(
            to_emails=self.test_email,
            template_id=template_id,
            dynamic_data=dynamic_data
        )
        
        # Assert the email was sent successfully
        self.assertTrue(result['success'])
        self.assertEqual(result['status_code'], 202)
        
        # Verify SendGrid was called
        mock_sendgrid.return_value.send.assert_called_once()
        
    @patch('services.email_service.SendGridAPIClient')
    def test_send_verification_email(self, mock_sendgrid):
        # Mock the SendGrid client response
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_sendgrid.return_value.send.return_value = mock_response
        
        # Test sending a verification email
        result = self.email_service.send_verification_email(
            to_email=self.test_email,
            verification_code="123456"
        )
        
        # Assert the email was sent successfully
        self.assertTrue(result['success'])
        self.assertEqual(result['status_code'], 202)
        
        # Verify SendGrid was called
        mock_sendgrid.return_value.send.assert_called_once()
        
    @patch('services.email_service.SendGridAPIClient')
    def test_send_password_reset_email(self, mock_sendgrid):
        # Mock the SendGrid client response
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_sendgrid.return_value.send.return_value = mock_response
        
        # Test sending a password reset email
        result = self.email_service.send_password_reset_email(
            to_email=self.test_email,
            reset_code="123456"
        )
        
        # Assert the email was sent successfully
        self.assertTrue(result['success'])
        self.assertEqual(result['status_code'], 202)
        
        # Verify SendGrid was called
        mock_sendgrid.return_value.send.assert_called_once()
        
    @patch('services.email_service.SendGridAPIClient')
    def test_error_handling(self, mock_sendgrid):
        # Mock SendGrid to raise an exception
        mock_sendgrid.return_value.send.side_effect = Exception("API Error")
        
        # Test sending an email that will fail
        result = self.email_service.send_email(
            to_emails=self.test_email,
            subject="Test Email",
            html_content="<p>Test content</p>"
        )
        
        # Assert the error was handled properly
        self.assertFalse(result['success'])
        self.assertIn("Failed to send email", result['message']) 