from django.urls import path

from .views import (AddQuestionsAPIView, ExamCreateView, LoginAPIView, Ping,
                    QuestionsAPIView, RestExamView, StoreFeedbackAPIView,
                    StoreResponseAPIView, UserCSVExportView, UserCSVUploadView)

urlpatterns = [
    path('api/export/users/', UserCSVExportView.as_view(), name='export_users_csv'),
    path('api/upload/users/', UserCSVUploadView.as_view(), name='upload_users_csv'),
    path('api/create_exam/', ExamCreateView.as_view(), name='exam_create'),
    path('api/login', LoginAPIView.as_view(), name='login'),
    path('api/question', QuestionsAPIView.as_view(), name='fetch_questions'),
    path('api/question/add', AddQuestionsAPIView.as_view(), name='add_questions'),
    path('api/answer/submit', StoreResponseAPIView.as_view(), name='capture_response'),
    path('api/submit/feedback', StoreFeedbackAPIView.as_view(), name='capture_response'),
    path('api/exam/rest', RestExamView.as_view(), name='reset_exam'),
    path('api/ping', Ping.as_view(), name='ping')
]