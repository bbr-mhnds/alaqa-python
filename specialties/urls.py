from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SpecialtyViewSet

router = DefaultRouter()
router.register('specialties', SpecialtyViewSet, basename='specialty')

urlpatterns = [
    path('', include(router.urls)),
] 