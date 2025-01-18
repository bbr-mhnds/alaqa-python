from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from django_filters import rest_framework as django_filters
from django.core.exceptions import ObjectDoesNotExist
from .models import InstantAppointmentPrice
from .serializers import InstantAppointmentPriceSerializer
from .pagination import CustomPagination

class InstantAppointmentPriceFilter(django_filters.FilterSet):
    """
    Filter set for InstantAppointmentPrice model
    """
    min_duration = django_filters.NumberFilter(field_name='duration', lookup_expr='gte')
    max_duration = django_filters.NumberFilter(field_name='duration', lookup_expr='lte')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = InstantAppointmentPrice
        fields = ['duration']

class InstantAppointmentPriceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing instant appointment prices
    """
    queryset = InstantAppointmentPrice.objects.all().order_by('duration')
    serializer_class = InstantAppointmentPriceSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    filter_backends = [django_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = InstantAppointmentPriceFilter
    ordering_fields = ['duration', 'price', 'created_at']
    ordering = ['duration']

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "status": "success",
                "message": "Price created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                "status": "error",
                "message": "Validation error",
                "errors": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
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
                    "prices": serializer.data
                }
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                "status": "success",
                "data": serializer.data
            })
        except ObjectDoesNotExist:
            return Response({
                "status": "error",
                "message": "Price not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                "status": "success",
                "message": "Price updated successfully",
                "data": serializer.data
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
                "message": "Price not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                "status": "success",
                "message": "Price deleted successfully"
            }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({
                "status": "error",
                "message": "Price not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return Response({
            "status": "success",
            "data": {
                "prices": data,
                "pagination": {
                    'count': self.paginator.page.paginator.count,
                    'total_pages': self.paginator.page.paginator.num_pages,
                    'current_page': self.paginator.page.number,
                    'page_size': self.paginator.page_size,
                    'next': self.paginator.get_next_link(),
                    'previous': self.paginator.get_previous_link()
                }
            }
        })
