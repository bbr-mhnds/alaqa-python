from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Token
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    TokenSerializer,
    ChangePasswordSerializer,
    ResetPasswordRequestSerializer,
    UpdateProfileSerializer,
)

User = get_user_model()

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def check_session(self, request):
        """Check if the user's session is valid and return user data"""
        user = request.user
        return Response({
            'status': 'success',
            'data': {
                'user': UserSerializer(user).data,
                'is_authenticated': True
            }
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], serializer_class=RegisterSerializer)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response({
            'status': 'success',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': tokens
            }
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], serializer_class=LoginSerializer)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if not user:
            return Response({
                'status': 'error',
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response({
            'status': 'success',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': tokens
            }
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'status': 'success',
                'message': 'Successfully logged out'
            })
        except Exception:
            return Response({
                'status': 'error',
                'message': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], serializer_class=ResetPasswordRequestSerializer)
    def password_reset(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
            # Generate a random password
            import string
            import random
            new_password = ''.join(random.choices(string.ascii_letters + string.digits + '@#$%^&*', k=12))
            
            # Set the new password
            user.set_password(new_password)
            user.save()
            
            # TODO: Send email with new password
            # For now, return the password in response (only for development)
            return Response({
                'status': 'success',
                'message': 'Password has been reset successfully',
                'data': {
                    'new_password': new_password  # Remove this in production
                }
            })
        except User.DoesNotExist:
            # Don't reveal whether a user exists
            return Response({
                'status': 'success',
                'message': 'If the email exists, a password reset email will be sent'
            })

    @action(detail=False, methods=['post'], serializer_class=ChangePasswordSerializer, permission_classes=[IsAuthenticated])
    def password_change(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['current_password']):
            return Response({
                'status': 'error',
                'message': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({
            'status': 'success',
            'message': 'Password changed successfully'
        })

class ProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response({
            'status': 'success',
            'data': {
                'user': serializer.data
            }
        })

    @action(detail=False, methods=['put'], serializer_class=UpdateProfileSerializer)
    def update_profile(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': 'success',
            'data': {
                'user': UserSerializer(request.user).data
            }
        })
