from functools import wraps
from django.core.exceptions import FieldError
from django.db import DatabaseError
from rest_framework.response import Response
from rest_framework import status

from .constants import INVALID_CREDENTIALS
from .models import User, Exam


def exception_handler_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except User.DoesNotExist:
            return Response({
                'error': INVALID_CREDENTIALS,
                'is_success': False
            }, status=status.HTTP_401_UNAUTHORIZED)

        except Exam.MultipleObjectsReturned:
            return Response({
                'error': 'Multiple Exam entries found with the given prefix.',
                'is_success': False
            }, status=status.HTTP_409_CONFLICT)

        except FieldError:
            return Response({
                'error': 'Field error in query.',
                'is_success': False
            }, status=status.HTTP_404_NOT_FOUND)

        except DatabaseError:
            return Response({
                'error': 'Database error occurred.',
                'is_success': False
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'error': str(e),
                'is_success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return wrapper
