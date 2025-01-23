from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DoctorViewSet,
    DoctorRegistrationViewSet,
    DoctorApprovalViewSet
)

app_name = 'doctors'

router = DefaultRouter()
router.register(r'', DoctorViewSet, basename='doctor')

registration_router = DefaultRouter()
registration_router.register(r'register', DoctorRegistrationViewSet, basename='doctor-registration')

approval_router = DefaultRouter()
approval_router.register(r'approve', DoctorApprovalViewSet, basename='doctor-approval')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(registration_router.urls)),
    path('', include(approval_router.urls)),
] 