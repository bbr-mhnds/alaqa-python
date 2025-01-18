from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntegrationViewSet, AgoraIntegrationViewSet, agora_callback

router = DefaultRouter()
router.register(r'integrations', IntegrationViewSet)
router.register(r'agora', AgoraIntegrationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('agora/callback/', agora_callback, name='agora-callback'),
] 