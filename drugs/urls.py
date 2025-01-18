from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DrugViewSet, DrugCategoryViewSet, DrugDosageFormViewSet

router = DefaultRouter()
# Register categories and dosage forms first
router.register(r"categories", DrugCategoryViewSet, basename="drug-category")
router.register(r"dosage-forms", DrugDosageFormViewSet, basename="drug-dosage-form")
# Register the main drug viewset last
router.register(r"", DrugViewSet, basename="drug")

urlpatterns = [
    path("", include(router.urls)),
] 