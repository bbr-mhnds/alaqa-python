from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.core.paginator import EmptyPage, PageNotAnInteger

class CustomPagination(PageNumberPagination):
    """
    Custom pagination class that handles both page and limit parameters
    with proper error handling and validation.
    """
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_page_size = 100
    page_size = 10

    def paginate_queryset(self, queryset, request, view=None):
        """
        Override paginate_queryset to handle pagination errors gracefully
        """
        try:
            self.page_size = self.get_page_size(request)
            return super().paginate_queryset(queryset, request, view)
        except Exception:
            if not queryset.exists():
                self.page = None
                return []
            try:
                page_number = 1
                paginator = self.django_paginator_class(queryset, self.page_size)
                self.page = paginator.page(page_number)
                return list(self.page)
            except Exception:
                self.page = None
                return []

    def get_paginated_response(self, data):
        """
        Return paginated response in a consistent format
        """
        if not self.page:
            return Response({
                'status': 'success',
                'data': {
                    'specialties': data,
                    'pagination': {
                        'count': 0,
                        'total_pages': 0,
                        'current_page': 1,
                        'page_size': self.page_size,
                        'next': None,
                        'previous': None
                    }
                }
            })

        return Response({
            'status': 'success',
            'data': {
                'specialties': data,
                'pagination': {
                    'count': self.page.paginator.count,
                    'total_pages': self.page.paginator.num_pages,
                    'current_page': self.page.number,
                    'page_size': self.page_size,
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                }
            }
        })

    def get_page_size(self, request):
        """
        Get and validate the page size
        """
        try:
            page_size = request.query_params.get(self.page_size_query_param, self.page_size)
            return min(int(page_size), self.max_page_size)
        except (ValueError, TypeError):
            return self.page_size 