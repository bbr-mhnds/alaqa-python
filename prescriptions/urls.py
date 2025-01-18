from django.urls import path, include
from rest_framework_nested import routers
from .views import PrescriptionViewSet, PrescribedDrugViewSet, TestRecommendationViewSet

# Create a router for prescriptions
router = routers.DefaultRouter()
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')

# Create nested routers for prescribed drugs and test recommendations
prescriptions_router = routers.NestedDefaultRouter(router, r'prescriptions', lookup='prescription')
prescriptions_router.register(r'drugs', PrescribedDrugViewSet, basename='prescription-drug')
prescriptions_router.register(r'tests', TestRecommendationViewSet, basename='prescription-test')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(prescriptions_router.urls)),
] 