from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import InstantAppointmentPriceViewSet

app_name = 'instant_appointment_prices'

router = DefaultRouter()
router.register('', InstantAppointmentPriceViewSet, basename='instant-appointment-price')

urlpatterns = router.urls 