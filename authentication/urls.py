from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import AuthViewSet, ProfileViewSet

router = DefaultRouter()
router.register(r'', AuthViewSet, basename='auth')
router.register(r'profile', ProfileViewSet, basename='profile')

check_session = AuthViewSet.as_view({'get': 'check_session'})

urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('check-session/', check_session, name='check-session'),
] 