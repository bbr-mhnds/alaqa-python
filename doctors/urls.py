from django.urls import path, include
from rest_framework_nested import routers
from .views import (
    DoctorViewSet,
    DoctorRegistrationViewSet,
    DoctorApprovalViewSet,
    DoctorBankDetailsViewSet,
    DoctorScheduleViewSet,
    DoctorPriceCategoryViewSet
)

app_name = 'doctors'

# Main router
router = routers.DefaultRouter()
router.register('', DoctorViewSet, basename='doctor')

# Registration router
registration_router = routers.DefaultRouter()
registration_router.register('register', DoctorRegistrationViewSet, basename='doctor-registration')

# Approval router
approval_router = routers.DefaultRouter()
approval_router.register('approve', DoctorApprovalViewSet, basename='doctor-approval')

# Bank details URLs with email lookup
urlpatterns = [
    path('', include(router.urls)),
    path('', include(registration_router.urls)),
    path('', include(approval_router.urls)),
    path('<str:doctor_email>/bank-details/', DoctorBankDetailsViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='doctor-bank-details-list'),
    path('<str:doctor_email>/bank-details/<uuid:pk>/', DoctorBankDetailsViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='doctor-bank-details-detail'),
    path('<str:doctor_email>/schedules/', DoctorScheduleViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='doctor-schedule-list'),
    path('<str:doctor_email>/price-categories/', DoctorPriceCategoryViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='doctor-price-category-list'),
    path('<str:doctor_email>/price-categories/<int:pk>/', DoctorPriceCategoryViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='doctor-price-category-detail'),
    path('<str:doctor_email>/duration-prices/', DoctorPriceCategoryViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='doctor-duration-prices-list'),
    path('<str:doctor_email>/duration-prices/<int:pk>/', DoctorPriceCategoryViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='doctor-duration-prices-detail'),
] 