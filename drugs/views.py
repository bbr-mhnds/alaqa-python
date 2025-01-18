from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from .models import Drug, DrugCategory, DrugDosageForm
from .serializers import (
    DrugListSerializer,
    DrugCreateSerializer,
    DrugUpdateSerializer,
    DrugStatusUpdateSerializer,
    DrugCategorySerializer,
    DrugDosageFormSerializer,
)


class DrugViewSet(viewsets.ModelViewSet):
    queryset = Drug.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = DrugListSerializer
    http_method_names = ["get", "post", "put", "patch", "delete"]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search functionality
        search = self.request.query_params.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(name_arabic__icontains=search) |
                Q(description__icontains=search) |
                Q(description_arabic__icontains=search)
            )

        # Status filter
        status_param = self.request.query_params.get("status")
        if status_param is not None:
            status_value = status_param.lower() == "true"
            queryset = queryset.filter(status=status_value)

        # Category filter
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category_id=category)

        return queryset.select_related("category", "dosage_form")

    def get_serializer_class(self):
        if self.action == "create":
            return DrugCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return DrugUpdateSerializer
        elif self.action == "update_status":
            return DrugStatusUpdateSerializer
        return DrugListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "status": "success",
                "data": {
                    "drugs": serializer.data
                }
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "data": {
                "drugs": serializer.data
            }
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Get the full drug data with expanded relations
        drug = Drug.objects.select_related("category", "dosage_form").get(id=serializer.instance.id)
        response_serializer = DrugListSerializer(drug)
        
        return Response({
            "status": "success",
            "data": {
                "drug": response_serializer.data
            }
        }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = DrugListSerializer(instance)
        return Response({
            "status": "success",
            "data": {
                "drug": serializer.data
            }
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Get the full drug data with expanded relations
        drug = Drug.objects.select_related("category", "dosage_form").get(id=instance.id)
        response_serializer = DrugListSerializer(drug)

        return Response({
            "status": "success",
            "data": {
                "drug": response_serializer.data
            }
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": "success",
            "message": _("Drug deleted successfully")
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            "status": "success",
            "data": {
                "drug": {
                    "id": instance.id,
                    "status": serializer.validated_data["status"],
                    "updated_at": instance.updated_at
                }
            }
        })


class DrugCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DrugCategory.objects.filter(status=True)
    serializer_class = DrugCategorySerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "data": {
                "categories": serializer.data
            }
        })


class DrugDosageFormViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DrugDosageForm.objects.filter(status=True)
    serializer_class = DrugDosageFormSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "data": {
                "dosageForms": serializer.data
            }
        })
