from rest_framework import serializers

from .models import Exam, User


class UserCSVSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'
