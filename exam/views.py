import csv
import json
import random

import uuid
from datetime import timedelta

import redis
from dateutil import parser
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from exam.constants import USER_ALREADY_EXISTS, USER_CREATED_SUCCESSFULLY, EXAM_PREFIX_NOT_FOUND, \
    MISSING_REQUIRED_FIELD, ALREADY_LOGGED_IN, INVALID_CREDENTIALS, CustomRedisException, USERNAME_MISSING, \
    USER_NOT_LOGGED_IN
from .cache import RedisManagerClient
from .models import Exam, User
from .serializers import CSVUploadSerializer, ExamSerializer, UserCSVSerializer
from .utils import exception_handler_decorator, question_bank_network_call

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

redis_client = RedisManagerClient().client


class UserCSVExportView(APIView):
    def get(self, request):
        # get student data in desc order of marks
        users = User.objects.all().order_by('-marks')
        serializer = UserCSVSerializer(users, many=True)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'

        writer = csv.writer(response)
        for user in serializer.data:
            writer.writerow([user])

        return response


class UserCSVUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        exam_prefix = request.data.get('exam_prefix', '')
        serializer = CSVUploadSerializer(data=request.data)

        if exam_prefix == '' or exam_prefix is None:
            return Response({
                "error": EXAM_PREFIX_NOT_FOUND
            },
                status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():
            file = request.FILES['file']
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            try:
                for row in reader:
                    user = User(
                        student_name=row['student_name'],
                        university_email=row['university_email'],
                        university_id=row['university_id'],
                        exam_prefix=exam_prefix,
                        username=exam_prefix + row['university_id']
                    )
                    user.save()

            except IntegrityError as ex:
                return Response({
                    "message": USER_ALREADY_EXISTS,
                    "error": str(ex)
                },
                    status=status.HTTP_400_BAD_REQUEST
                )

            except Exception as ex:
                return Response({
                    "error": str(ex)
                },
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                "message": USER_CREATED_SUCCESSFULLY},
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ExamCreateView(generics.CreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

    def perform_create(self, serializer):
        valid_till_str = self.request.data.get('valid_till')
        if valid_till_str:
            valid_till = parser.isoparse(valid_till_str)
            # If the parsed valid_till is naive (no timezone), make it aware
            if valid_till.tzinfo is None:
                valid_till = timezone.make_aware(valid_till, timezone.get_current_timezone())
        else:
            valid_till = timezone.now() + timedelta(days=14)
        serializer.save(
            created_at=timezone.now(),
            valid_till=valid_till,
            prefix=''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 2)) + '_'
        )


class LoginAPIView(APIView):
    @exception_handler_decorator
    def post(self, request):
        username = request.data.get('username')
        exam_prefix = username.split('_')[0] + '_'

        if username is None or username == '':
            return Response(
                {
                    'error': MISSING_REQUIRED_FIELD,
                    'is_success': False
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():  # so entire code can be roll back
            user = User.objects.select_for_update().get(username=username)  # locks the row in DB
            if user.last_logged_in is None:
                user.last_logged_in = timezone.now()
                user.auth_token = uuid.uuid4().hex
                user.save()

            else:
                return Response({
                    'error': ALREADY_LOGGED_IN,
                    'is_success': False
                }, status=status.HTTP_406_NOT_ACCEPTABLE)

            try:
                time_per_question = redis_client.get(f"tpq:{exam_prefix}")
                no_of_questions = redis_client.get(f"tq:{exam_prefix}")

                if time_per_question is None or no_of_questions is None:
                    raise CustomRedisException()

            except CustomRedisException:
                exam_obj = Exam.objects.get(prefix=exam_prefix)
                time_per_question = exam_obj.time_per_question
                no_of_questions = exam_obj.no_of_questions

                redis_client.set(f"tpq:{exam_prefix}", time_per_question)
                redis_client.set(f"noq:{exam_prefix}", no_of_questions)

            except (
                    redis.ConnectionError,
                    redis.TimeoutError,
                    redis.RedisError,
                    AttributeError
            ):
                exam_obj = Exam.objects.get(prefix=exam_prefix)
                time_per_question = exam_obj.time_per_question
                no_of_questions = exam_obj.no_of_questions

            return Response({
                'status': 'User logged in',
                'is_success': True,
                'token': user.auth_token,
                "time_per_question": time_per_question,
                "total_questions": no_of_questions
            }, status=status.HTTP_200_OK)


class RequestQuestionsAPIView(APIView):
    @exception_handler_decorator
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        try:
            username = body_data['username']

        except KeyError:
            return Response({
                "error": USERNAME_MISSING,
                "is_success": False
            },
                status=status.HTTP_400_BAD_REQUEST
            )

        if '_' in username:
            exam_prefix = username.split('_')[0] + '_'

        else:
            return Response({
                "error": MISSING_REQUIRED_FIELD.format("exam_prefix"),
                "is_success": False
            },
                status=status.HTTP_400_BAD_REQUEST)

        # check if auth token is correct
        try:
            User.objects.get(
                auth_token=body_data.get("token"),
                username=username
            )

        except User.DoesNotExist:
            Response({
                    'error': USER_NOT_LOGGED_IN,
                    'is_success': False
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            no_of_questions = redis_client.get(f"noq:{exam_prefix}")
            if no_of_questions is None:
                raise CustomRedisException()

        except CustomRedisException:
            no_of_questions = Exam.objects.get(
                prefix=exam_prefix
            ).no_of_questions

            # set it to redis
            redis_client.set(f'noq:{exam_prefix}', no_of_questions)

        except (
                redis.ConnectionError,
                redis.TimeoutError,
                redis.RedisError,
                AttributeError
        ):
            no_of_questions = Exam.objects.get(
                prefix=exam_prefix
            ).no_of_questions

        response = question_bank_network_call({
                                            "username": username,
                                            "question_limit": no_of_questions
                                        },
            "GET",
            "/question"
        )

        if not response.get("error"):
            data = {
                'question_id': response['question_id'],
                'text': response['text'],
                'options': response['options']
            }

        else:
            data = {
                'error': response.get("error") if response else 'Failed to fetch questions from microservice',
                'is_success': False
            }

        if data.get('is_success') is False:
            return Response(
                data,
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(data)


class AddQuestionsAPIView(APIView):

    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)

            response = question_bank_network_call(body_data, "POST", "/question/add")
            return Response(
                response,
                status=status.HTTP_200_OK if response.get("message") else status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": str(e)}
            )


class StoreResponseAPIView(APIView):

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        if not body_data:
            return Response(
                data={
                    "error": "No data to submit",
                    "status": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        response = question_bank_network_call(body_data, "POST", "/answer/submit")

        if response.get("error"):
            return Response(
                data={
                    "error": response.get("error")
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            response,
            status=status.HTTP_200_OK
        )


class StoreFeedbackAPIView(APIView):

    def post(self, request):
        response = {
            "status": "success",
            "message": "Feedback submitted successfully"
        }

        try:
            body_data = json.loads(request.body.decode('utf-8'))
            response = question_bank_network_call(
                body_data,
                "POST",
                "/submit/feedback"
            )

        except json.decoder.JSONDecodeError:
            pass

        return Response(
            response,
            status=status.HTTP_200_OK
        )


class RestExamView(APIView):
    def post(self, request):
        username = request.data.get('username')
        if username is None:
            return Response({'error': 'username ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        # black list that auth token
        try:
            user = User.objects.get(username=username)

            if user.last_logged_in:
                user.last_logged_in = None
                user.auth_token = None
                user.marks = 0
                user.reset_count = user.reset_count + 1
                user.save()

                return Response({
                    'status': 'User reset done!',
                    'is_success': True,
                },
                    status=status.HTTP_200_OK
                )

            else:
                return Response({
                    'error': 'Already never logged in.',
                    'is_success': False
                }, status=status.HTTP_200_OK
                )

        except User.DoesNotExist:
            return Response({
                    'error': INVALID_CREDENTIALS,
                    'is_success': False
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        except Exception as ex:
            return Response({
                    'error': str(ex),
                    'is_success': False
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class Ping(APIView):
    def get(self, request):
        return Response({"ping": "pong"})
