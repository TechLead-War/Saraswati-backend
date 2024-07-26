import csv
import json
import os
import random
import uuid
from datetime import timedelta

import redis
import requests
from dateutil import parser
from django.core.exceptions import FieldError
from django.db import IntegrityError, DatabaseError
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from exam.constants import USER_ALREADY_EXISTS, USER_CREATED_SUCCESSFULLY, EXAM_PREFIX_NOT_FOUND, \
    MISSING_REQUIRED_FIELD, ALREADY_LOGGED_IN, INVALID_CREDENTIALS
from .cache import RedisManagerClient
from .models import Exam, User
from .serializers import CSVUploadSerializer, ExamSerializer, UserCSVSerializer
from .utils import exception_handler_decorator

question_bank_uri = os.getenv('QuestionBankAppURI', "http://127.0.0.1:5012")
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
    def post(self, request):
        username = request.data.get('username')
        exam_prefix = username.split('_')[0] + '_'

        try:
            user = User.objects.get(username=username)
            if user.last_logged_in is None:
                user.last_logged_in = timezone.now()
                user.auth_token = uuid.uuid4().hex
                user.save()

                try:
                    question_limits = redis_client.get(exam_prefix)
                    time_per_question = redis_client.get(f"tpq:{exam_prefix}")
                    total_questions = redis_client.get(f"tq:{exam_prefix}")

                    if question_limits is None:
                        question_limit = Exam.objects.get(prefix=exam_prefix).no_of_questions
                        redis_client.set(exam_prefix, question_limit)
                    else:
                        question_limit = int(question_limits)

                    if time_per_question is None:
                        time_per_question = Exam.objects.get(prefix=exam_prefix).time_per_question
                        redis_client.set(f"tpq:{exam_prefix}", time_per_question)
                    else:
                        time_per_question = int(time_per_question)

                    if total_questions is None:
                        total_questions = Exam.objects.get(prefix=exam_prefix).total_questions
                        redis_client.set(f"tq:{exam_prefix}", total_questions)

                    else:
                        total_questions = int(time_per_question)

                except (
                        redis.ConnectionError,
                        redis.TimeoutError,
                        redis.RedisError,
                        AttributeError
                ):
                    exam_obj = Exam.objects.get(prefix=exam_prefix)
                    question_limit = exam_obj.no_of_questions
                    time_per_question = exam_obj.time_per_question
                    total_questions = exam_obj.no_of_questions

                return Response({
                    'status': 'User logged in',
                    'is_success': True,
                    'token': user.auth_token,
                    "question_limit": question_limit,
                    "time_per_question": time_per_question,
                    "total_questions": total_questions
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    'error': 'Already logged in',
                    'is_success': False
                }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                'error': 'Invalid credentials',
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


class QuestionsAPIView(APIView):

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        username = body_data['username']
        exam_id = username.split('_')[0] + '_'

        try:
            # check if auth token is correct
            User.objects.get(
                auth_token=body_data.get("token"),
                username=username
            )

            try:
                redis_response = redis_client.get(f'QL:{exam_id}')

                if redis_response is None:
                    question_limit = Exam.objects.get(
                        prefix=exam_id
                    ).no_of_questions
                    # set it to redis
                    redis_client.set(f'QL:{exam_id}', question_limit)

                else:
                    question_limit = redis_response

            except Exception:
                # redis is not reachable
                question_limit = Exam.objects.get(
                    prefix=exam_id
                ).no_of_questions

            # Call the microservice to get questions
            microservice_url = f"{question_bank_uri}/question"
            headers = {
                'Authorization': f'Bearer {os.getenv("ADMIN_TOKEN")}',  # Add the admin token in the headers
                'Content-Type': 'application/json'
            }
            try:
                response = requests.get(
                    microservice_url,
                    headers=headers,
                    params={
                        "username": username,
                        "question_limit": question_limit
                    }
                )

            except Exception as e:
                pass

            if "response" in vars() and response.status_code == 200:
                questions = response.json()
                data = {
                    'question_id': questions['question_id'],
                    'text': questions['text'],
                    'options': questions['options']
                }

            elif response.status_code == 409:
                data = {
                    'error': response.json(),
                    'is_success': False
                }
                return Response(data, status=status.HTTP_409_CONFLICT)

            else:
                if response:
                    data = {
                        'error': response.json(),
                        'is_success': False
                    }
                else:
                    data = {
                        'error': 'Failed to fetch questions from microservice',
                        'is_success': False
                    }

        except User.DoesNotExist:
            data = {
                'error': 'User not logged in / or invalid token',
                'is_success': False
            }

        if data.get('is_success') is False:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        return Response(data)


class AddQuestionsAPIView(APIView):

    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            auth_token = request.headers.get('Authorization')

            if auth_token == f'Bearer ' + os.getenv('ADMIN_TOKEN'):
                # Call the microservice to get questions
                microservice_url = f"{question_bank_uri}/question/add"
                headers = {
                    'Authorization': f'Bearer {os.getenv("ADMIN_TOKEN")}',  # Add the admin token in the headers
                    'Content-Type': 'application/json'
                }

                response = requests.post(
                    microservice_url,
                    headers=headers,
                    json=body_data
                )
                if response.status_code == 201:
                    data = {
                        "message": "Question added successfully",
                        "status": status.HTTP_201_CREATED
                    }
                    status_res = status.HTTP_201_CREATED

                else:
                    data = response.json()
                    status_res = status.HTTP_400_BAD_REQUEST

                return Response(data, status=status_res)

            else:
                return Response(
                    data={
                        "error": "Invalid auth token"
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except Exception as e:
            return Response(
                status=200,
                data={"error": str(e)}
            )


class StoreResponseAPIView(APIView):

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        auth_token = request.headers.get('Authorization')

        if auth_token == f'Bearer ' + os.getenv('ADMIN_TOKEN'):
            # Call the microservice to get questions
            microservice_url = f"{question_bank_uri}/answer/submit"
            headers = {
                'Authorization': f'Bearer {os.getenv("ADMIN_TOKEN")}',  # Add the admin token in the headers
                'Content-Type': 'application/json'
            }
            response = requests.post(
                microservice_url,
                headers=headers,
                json=body_data
            )

            if response.status_code == 200:
                data = {
                    "message": "Response captured successfully",
                    "status": status.HTTP_200_OK
                }

            else:
                data = response.json()

            return Response(data, status=status.HTTP_200_OK)


class StoreFeedbackAPIView(APIView):

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        auth_token = request.headers.get('Authorization')

        if auth_token == f'Bearer ' + os.getenv('ADMIN_TOKEN'):
            # Call the microservice to get questions
            microservice_url = f"{question_bank_uri}/submit/feedback"
            headers = {
                'Authorization': f'Bearer {os.getenv("ADMIN_TOKEN")}',  # Add the admin token in the headers
                'Content-Type': 'application/json'
            }

            response = requests.post(
                microservice_url,
                headers=headers,
                json=body_data
            )

            if response.status_code == 200:
                data = {
                    "message": "Response captured successfully",
                    "status": status.HTTP_200_OK
                }

            else:
                data = response.json()

            return Response(data, status=status.HTTP_200_OK)


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
            return Response({'error': 'Invalid credentials', 'is_success': False}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({'error': str(e), 'is_success': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Ping(APIView):
    def get(self, request):
        return Response({"ping": "pong"})
