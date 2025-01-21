from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DoctorViewSet,
    DoctorRegistrationViewSet,
    DoctorApprovalViewSet
)

app_name = 'doctors'

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet)
router.register(r'register', DoctorRegistrationViewSet)
router.register(r'approve', DoctorApprovalViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 