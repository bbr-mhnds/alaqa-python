from django.shortcuts import render
from rest_framework import viewsets, status, filters, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters import rest_framework as django_filters
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from .models import Specialty
from .serializers import SpecialtySerializer
from .pagination import CustomPagination

class SpecialtyFilter(django_filters.FilterSet):
    """
    FilterSet for Specialty model with custom search functionality
    """
    status = django_filters.BooleanFilter()
    search = django_filters.CharFilter(method='search_filter')

    class Meta:
        model = Specialty
        fields = ['status']

    def search_filter(self, queryset, name, value):
        """
        Custom search filter that searches in both English and Arabic titles
        """
        if value:
            return queryset.filter(
                models.Q(title__icontains=value) |
                models.Q(title_ar__icontains=value)
            )
        return queryset

class SpecialtyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing specialties with pagination and filtering.
    List and retrieve actions are public, while other actions require authentication.
    """
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    filterset_class = SpecialtyFilter
    pagination_class = CustomPagination
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    ordering_fields = ['id', 'title', 'title_ar']
    ordering = ['id']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Get the list of items for this view with proper ordering
        """
        queryset = super().get_queryset().order_by('id')
        if self.action == 'list':
            return queryset.filter(status=True)
        return queryset

    def list(self, request, *args, **kwargs):
        """
        List specialties with pagination and filtering
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": "success",
                "data": {
                    "specialties": serializer.data,
                    "pagination": None
                }
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single specialty
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                "status": "success",
                "data": {
                    "specialty": serializer.data
                }
            })
        except ObjectDoesNotExist:
            return Response({
                "status": "error",
                "message": "Specialty not found"
            }, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """
        Create a new specialty
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "status": "success",
                "data": {
                    "specialty": serializer.data
                }
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                "status": "error",
                "message": "Validation error",
                "errors": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Update a specialty
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                "status": "success",
                "data": {
                    "specialty": serializer.data
                }
            })
        except ValidationError as e:
            return Response({
                "status": "error",
                "message": "Validation error",
                "errors": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({
                "status": "error",
                "message": "Specialty not found"
            }, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a specialty
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                "status": "success",
                "message": "Specialty deleted successfully"
            }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({
                "status": "error",
                "message": "Specialty not found"
            }, status=status.HTTP_404_NOT_FOUND)
