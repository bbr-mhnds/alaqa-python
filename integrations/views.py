from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import hmac
import hashlib
import json
from .models import Integration, AgoraIntegration, IntegrationLog, IntegrationCredential
from .serializers import (
    IntegrationSerializer, AgoraIntegrationSerializer,
    IntegrationStatusSerializer, IntegrationLogSerializer
)
from .services import AgoraService
import logging
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class IntegrationViewSet(viewsets.ModelViewSet):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return self.queryset.prefetch_related('credentials', 'logs')
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle the integration's enabled status"""
        integration = self.get_object()
        integration.is_enabled = not integration.is_enabled
        integration.save()
        return Response(IntegrationStatusSerializer(integration).data)
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get integration logs with optional filtering"""
        integration = self.get_object()
        logs = integration.logs.all()
        
        # Filter by level if specified
        level = request.query_params.get('level')
        if level:
            logs = logs.filter(level=level)
            
        # Filter by date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            logs = logs.filter(created_at__gte=start_date)
        if end_date:
            logs = logs.filter(created_at__lte=end_date)
            
        page = self.paginate_queryset(logs)
        serializer = IntegrationLogSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

class AgoraIntegrationViewSet(viewsets.ModelViewSet):
    queryset = AgoraIntegration.objects.all()
    serializer_class = AgoraIntegrationSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return self.queryset.prefetch_related('credentials', 'logs')
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test the Agora integration connection"""
        integration = self.get_object()
        
        try:
            # Try to generate a test token
            token, expiration = AgoraService.generate_token(
                channel_name="test_channel",
                uid=1
            )
            
            # Log success
            IntegrationLog.objects.create(
                integration=integration,
                level='info',
                message='Successfully tested Agora connection',
                metadata={
                    'test_channel': "test_channel",
                    'expiration': timezone.datetime.fromtimestamp(expiration).isoformat()
                },
                user=request.user
            )
            
            integration.mark_active()
            return Response({
                'status': 'success',
                'message': 'Successfully connected to Agora'
            })
            
        except Exception as e:
            # Log error
            error_message = str(e)
            IntegrationLog.objects.create(
                integration=integration,
                level='error',
                message=f'Failed to test Agora connection: {error_message}',
                user=request.user
            )
            
            integration.record_error(error_message)
            return Response({
                'status': 'error',
                'message': error_message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_settings(self, request, pk=None):
        """Update Agora integration settings"""
        integration = self.get_object()
        serializer = self.get_serializer(integration, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Log the settings update
            IntegrationLog.objects.create(
                integration=integration,
                level='info',
                message='Settings updated',
                metadata={'updated_fields': list(request.data.keys())},
                user=request.user
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@require_http_methods(["POST"])
def agora_callback(request):
    """Handle Agora authentication callback"""
    
    try:
        # Get request body
        try:
            data = json.loads(request.body.decode())
            logger.debug(f'Parsed JSON data: {data}')
        except json.JSONDecodeError as e:
            logger.error(f'Invalid JSON payload: {str(e)}')
            return JsonResponse(
                {'error': 'Invalid JSON payload'},
                status=400
            )
        
        # Verify signature if webhook secret is configured
        if hasattr(settings, 'AGORA_WEBHOOK_SECRET'):
            signature = request.headers.get('X-Agora-Signature')
            
            if not signature:
                logger.error('Missing signature in request headers')
                return JsonResponse(
                    {'error': 'Missing signature'},
                    status=401
                )
                
            # Create signature
            payload = json.dumps(data, separators=(',', ':'))
            
            expected_signature = hmac.new(
                settings.AGORA_WEBHOOK_SECRET.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.error('Invalid signature')
                return JsonResponse(
                    {'error': 'Invalid signature'},
                    status=401
                )
        
        # Get or create Agora integration
        try:
            integration = AgoraIntegration.objects.get(is_enabled=True)
            logger.debug('Updating existing Agora integration')
            # Update existing integration
            integration.app_id = data.get('app_id', integration.app_id)
            integration.app_certificate = data.get('app_certificate', integration.app_certificate)
            integration.save()
        except AgoraIntegration.DoesNotExist:
            logger.debug('Creating new Agora integration')
            integration = AgoraIntegration.objects.create(
                name='Agora Integration',
                description='Automatically configured Agora integration',
                is_enabled=True,
                app_id=data.get('app_id'),
                app_certificate=data.get('app_certificate'),
                token_expiration_time=3600,  # Default 1 hour
                max_users_per_channel=4  # Default max users
            )
        
        # Save additional credentials if provided
        credentials = data.get('credentials', {})
        for key, value in credentials.items():
            logger.debug(f'Saving credential: {key}')
            IntegrationCredential.objects.update_or_create(
                integration=integration,
                key=key,
                defaults={'value': value}
            )
        
        # Save configurations
        config = data.get('config', {})
        if config:
            logger.debug(f'Updating configuration: {config}')
            for key, value in config.items():
                if hasattr(integration, key):
                    setattr(integration, key, value)
            integration.save()
        
        # Log success
        IntegrationLog.objects.create(
            integration=integration,
            level='info',
            message='Successfully updated Agora configuration via callback',
            metadata={'config_keys': list(config.keys()) if config else []}
        )
        
        # Clear cache to ensure new settings are used
        AgoraService.clear_cache()
        
        # Mark integration as active
        integration.mark_active()
        logger.debug('Integration marked as active')
        
        return JsonResponse({
            'status': 'success',
            'message': 'Configuration updated successfully'
        })
        
    except ValidationError as e:
        logger.error(f'Validation error in agora_callback: {str(e)}')
        return JsonResponse(
            {'error': str(e)},
            status=400
        )
    except Exception as e:
        logger.error(f'Error in agora_callback: {str(e)}', exc_info=True)
        # Log error
        if 'integration' in locals():
            integration.record_error(str(e))
            IntegrationLog.objects.create(
                integration=integration,
                level='error',
                message=f'Failed to process callback: {str(e)}'
            )
        
        return JsonResponse(
            {'error': str(e)},
            status=500
        )
