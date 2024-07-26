import os

from django.utils.deprecation import MiddlewareMixin
from django.db import connection


class SetSearchPathMiddleware(MiddlewareMixin):
    def process_request(self, request):
            with connection.cursor() as cursor:
                cursor.execute(f'SET search_path TO {os.getenv("SERVICE_DATABASE_SEARCH_PATH")}, public;')
