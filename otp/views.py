import logging
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .services import OTPService

logger = logging.getLogger(__name__)

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """
    Send OTP to the provided phone number
    """
    logger.info("[OTP_DEBUG] Received send_otp request")
    logger.info(f"[OTP_DEBUG] Request Method: {request.method}")
    logger.info(f"[OTP_DEBUG] Request Headers: {dict(request.headers)}")
    logger.info(f"[OTP_DEBUG] Request Data: {request.data}")
    
    try:
        phone_number = request.data.get('phone_number')
        logger.info(f"[OTP_DEBUG] Extracted phone number: {phone_number}")
        
        if not phone_number:
            logger.error("[OTP_DEBUG] Phone number missing in request")
            return Response({
                'status': 'error',
                'message': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate phone number format
        phone_number = phone_number.strip().replace(' ', '')
        logger.info(f"[OTP_DEBUG] Sanitized phone number: {phone_number}")
        
        if not phone_number.isdigit() or len(phone_number) < 9:
            logger.error(f"[OTP_DEBUG] Invalid phone number format: {phone_number}")
            return Response({
                'status': 'error',
                'message': 'Invalid phone number format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send OTP
        logger.info("[OTP_DEBUG] Calling OTPService.create_and_send_otp")
        result = OTPService.create_and_send_otp(phone_number)
        logger.info(f"[OTP_DEBUG] OTPService result: {result}")
        
        if result['success']:
            response_data = {
                'status': 'success',
                'message': 'OTP sent successfully',
                'data': {
                    'otp_id': result['otp_id']
                }
            }
            logger.info(f"[OTP_DEBUG] Sending success response: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)
        
        logger.error(f"[OTP_DEBUG] Failed to send OTP: {result['message']}")
        return Response({
            'status': 'error',
            'message': result['message']
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.exception("[OTP_DEBUG] Unexpected error in send_otp view")
        return Response({
            'status': 'error',
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify the provided OTP code
    """
    logger.info("[OTP_DEBUG] Received verify_otp request")
    logger.info(f"[OTP_DEBUG] Request Method: {request.method}")
    logger.info(f"[OTP_DEBUG] Request Headers: {dict(request.headers)}")
    logger.info(f"[OTP_DEBUG] Request Data: {request.data}")
    
    try:
        phone_number = request.data.get('phone_number')
        otp_code = request.data.get('otp_code')
        logger.info(f"[OTP_DEBUG] Verifying OTP - Phone: {phone_number}, Code: {otp_code}")
        
        if not phone_number or not otp_code:
            logger.error("[OTP_DEBUG] Missing phone_number or otp_code in request")
            return Response({
                'status': 'error',
                'message': 'Phone number and OTP code are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate phone number format
        phone_number = phone_number.strip().replace(' ', '')
        logger.info(f"[OTP_DEBUG] Sanitized phone number: {phone_number}")
        
        if not phone_number.isdigit() or len(phone_number) < 9:
            logger.error(f"[OTP_DEBUG] Invalid phone number format: {phone_number}")
            return Response({
                'status': 'error',
                'message': 'Invalid phone number format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate OTP format
        otp_code = otp_code.strip()
        logger.info(f"[OTP_DEBUG] Sanitized OTP code: {otp_code}")
        
        if not otp_code.isdigit() or len(otp_code) != 6:
            logger.error(f"[OTP_DEBUG] Invalid OTP format: {otp_code}")
            return Response({
                'status': 'error',
                'message': 'Invalid OTP format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP
        logger.info("[OTP_DEBUG] Calling OTPService.verify_otp")
        success, message = OTPService.verify_otp(phone_number, otp_code)
        logger.info(f"[OTP_DEBUG] Verification result - Success: {success}, Message: {message}")
        
        if success:
            response_data = {
                'status': 'success',
                'message': message
            }
            logger.info(f"[OTP_DEBUG] Sending success response: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)
        
        logger.error(f"[OTP_DEBUG] Verification failed: {message}")
        return Response({
            'status': 'error',
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.exception("[OTP_DEBUG] Unexpected error in verify_otp view")
        return Response({
            'status': 'error',
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
