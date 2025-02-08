from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, complete_appointment

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
    path('appointments/<int:appointment_id>/complete/', complete_appointment, name='appointment-complete'),
] 