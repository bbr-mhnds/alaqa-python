from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoCallViewSet, generate_agora_token, refresh_agora_token

router = DefaultRouter()
router.register(r'video-calls', VideoCallViewSet, basename='video-calls')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', generate_agora_token, name='generate-token'),
    path('token/refresh/', refresh_agora_token, name='refresh-token'),
] 