import random
from datetime import timedelta

from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token


class Exam(models.Model):
    exam_id = models.BigAutoField(primary_key=True)
    exam_name = models.CharField(max_length=255)
    course_name = models.CharField(max_length=255, default="Engg.")
    created_at = models.DateTimeField(default=timezone.now)
    created_for = models.BigIntegerField()  # which year students or what occasion this is made for
    no_of_questions = models.BigIntegerField(default=10)
    valid_till = models.DateTimeField(default=timezone.now() + timedelta(days=14))
    prefix = models.CharField(max_length=5, default="")
    time_per_question = models.IntegerField(default=30)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.valid_till = timezone.now() + timedelta(days=14)
            self.course_name = "Engg."
        super().save(*args, **kwargs)

    def __str__(self):
        return self.exam_name


class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    university_id = models.BigIntegerField(null=True, unique=False)
    auth_token = models.CharField(max_length=36, null=True)
    last_logged_in = models.DateTimeField(null=True, blank=True)
    cdate = models.DateField(auto_now_add=True)
    marks = models.IntegerField(default=0)
    student_name = models.CharField(max_length=50, default="None")
    university_email = models.EmailField(default="None")
    reset_count = models.IntegerField(default=0)
    exam_prefix = models.CharField(max_length=3, default="NA")
    username = models.CharField(max_length=15, default="NA", unique=True)

    def __str__(self):
        return self.username
