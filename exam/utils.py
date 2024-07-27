from functools import wraps
from django.core.exceptions import FieldError
from django.db import DatabaseError
from rest_framework.response import Response
from rest_framework import status

from .constants import INVALID_CREDENTIALS
from .models import User, Exam

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def exception_handler_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except User.DoesNotExist as e:
            logger.info(e)
            return Response({
                'error': INVALID_CREDENTIALS,
                'is_success': False
            }, status=status.HTTP_401_UNAUTHORIZED)

        except Exam.MultipleObjectsReturned as e:
            logger.info(e)
            return Response({
                'error': 'Multiple Exam entries found with the given prefix.',
                'is_success': False
            }, status=status.HTTP_409_CONFLICT)

        except FieldError as e:
            logger.info(e)
            return Response({
                'error': 'Field error in query.',
                'is_success': False
            }, status=status.HTTP_404_NOT_FOUND)

        except DatabaseError as e:
            logger.info(e)
            return Response({
                'error': 'Database error occurred.',
                'is_success': False
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.info(e)
            return Response({
                'error': str(e),
                'is_success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return wrapper
