from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.db import models
from .models import Patient
from .serializers import PatientSerializer, PatientStatusSerializer

class PatientFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Patient.StatusChoices.choices)
    search = filters.CharFilter(method='search_filter')

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(name_arabic__icontains=value) |
            models.Q(email__icontains=value)
        )

    class Meta:
        model = Patient
        fields = ['status', 'search']

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filterset_class = PatientFilter
    search_fields = ['name', 'name_arabic', 'email']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "status": "success",
                "data": {
                    "patients": serializer.data,
                    "pagination": {
                        "total": self.paginator.page.paginator.count,
                        "pages": self.paginator.page.paginator.num_pages,
                        "page": self.paginator.page.number,
                        "limit": self.paginator.page_size
                    }
                }
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "data": {
                "patients": serializer.data
            }
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "status": "success",
            "data": {
                "patient": serializer.data
            }
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "status": "success",
                "data": {
                    "patient": serializer.data
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Invalid request parameters",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "status": "success",
                "data": {
                    "patient": serializer.data
                }
            })
        return Response({
            "status": "error",
            "message": "Invalid request parameters",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": "success",
            "message": "Patient deleted successfully"
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], serializer_class=PatientStatusSerializer)
    def status(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "data": {
                    "patient": serializer.data
                }
            })
        
        return Response({
            "status": "error",
            "message": "Invalid request parameters",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
