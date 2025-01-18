from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

def custom_exception_handler(exc, context):
    if isinstance(exc, Http404):
        exc = DRFValidationError({
            'detail': 'Resource not found'
        })
    elif isinstance(exc, PermissionDenied):
        exc = DRFValidationError({
            'detail': 'Permission denied'
        })
    elif isinstance(exc, DjangoValidationError):
        exc = DRFValidationError(exc.messages)

    response = exception_handler(exc, context)

    if response is not None:
        errors = []
        if isinstance(response.data, dict):
            for field, value in response.data.items():
                if isinstance(value, (list, tuple)):
                    errors.append({
                        'field': field,
                        'message': value[0]
                    })
                else:
                    errors.append({
                        'field': field,
                        'message': value
                    })
        elif isinstance(response.data, list):
            errors = [{'message': error} for error in response.data]

        error_response = {
            'status': 'error',
            'message': 'Validation error' if errors else 'An error occurred',
        }

        if errors:
            error_response['errors'] = errors

        response.data = error_response

    return response 