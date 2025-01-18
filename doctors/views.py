from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters import rest_framework as django_filters
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from .models import Doctor
from .serializers import DoctorSerializer, DoctorStatusSerializer

class DoctorFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status')
    specialty = django_filters.UUIDFilter(field_name='specialities__id')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Doctor
        fields = ['status', 'specialty']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(name_arabic__icontains=value) |
            models.Q(email__icontains=value)
        )

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    filterset_class = DoctorFilter
    filter_backends = [django_filters.DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        List and Retrieve endpoints are public
        Other actions require authentication
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter queryset based on action and user permissions
        Public endpoints only see approved doctors
        """
        queryset = super().get_queryset()
        
        # For public endpoints (list, retrieve), only show approved doctors
        if self.action in ['list', 'retrieve'] and not self.request.user.is_authenticated:
            queryset = queryset.filter(status='approved')
        
        return queryset.order_by(self.ordering[0])

    def list(self, request, *args, **kwargs):
        """
        List doctors with pagination and filtering
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response({
                    'status': 'success',
                    'data': {
                        'doctors': serializer.data,
                        'pagination': {
                            'total': self.paginator.page.paginator.count,
                            'pages': self.paginator.page.paginator.num_pages,
                            'page': self.paginator.page.number,
                            'limit': self.paginator.page_size
                        }
                    }
                })

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'data': {
                    'doctors': serializer.data
                }
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single doctor
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'status': 'success',
                'data': {
                    'doctor': serializer.data
                }
            })
        except ObjectDoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Doctor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        """
        Create a new doctor
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                'status': 'success',
                'message': 'Doctor created successfully',
                'data': {
                    'doctor': serializer.data
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Update a doctor
        """
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                'status': 'success',
                'message': 'Doctor updated successfully',
                'data': {
                    'doctor': serializer.data
                }
            })
        except ObjectDoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Doctor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a doctor
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                'status': 'success',
                'message': 'Doctor deleted successfully'
            }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Doctor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        try:
            instance = self.get_object()
            serializer = DoctorStatusSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Doctor status updated successfully',
                'data': {
                    'doctor': serializer.data
                }
            })
        except ObjectDoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Doctor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
