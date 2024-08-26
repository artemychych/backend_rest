from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Test, Question

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id', 
                  'username',
                  'password',
                  'email']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'type', 'text', 'options', 'correctAnswer', 
            'fileType', 'description', 'uploadedFile'
        ]

class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)  # Используем QuestionSerializer для вложенных вопросов

    class Meta:
        model = Test
        fields = ['id', 'title', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        test = Test.objects.create(**validated_data)

        for question_data in questions_data:
            # Извлекаем файл, если он есть
            uploaded_file = question_data.pop('uploaded_file', None)

            # Создаем вопрос, связанный с тестом
            question = Question.objects.create(test=test, **question_data)

            # Сохраняем файл, если он был передан
            if uploaded_file:
                question.uploaded_file = uploaded_file
                question.save()

        return test