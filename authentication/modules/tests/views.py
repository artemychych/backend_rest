import json
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ...models import *
from ...serializers import TestSerializer, QuestionSerializer
import mimetypes
from urllib.parse import quote as urlquote
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # Добавляем парсеры для FormData
def create_or_update_test(request):
    data = request.data
    files = request.FILES
    print(data)
    print(data.get('internship_id'))
    internship = Internship.objects.get(id=data.get('internship_id'))
    try:
        test = Test.objects.get(id=data.get('internship_id'))
        test.title = data.get('title')
        test.save()
    except Test.DoesNotExist:
        test = Test.objects.create(id=data.get('internship_id'), title=data.get('title'), internship=internship)

    print(internship)
    # Получаем или создаем объект Test
    # test, created = Test.objects.update_or_create(
    #     id=data.get('id'),
    #     defaults={'title': data.get('title')}
    # )
    prev_questions = Question.objects.filter(test=test)
    if prev_questions:
        prev_questions.delete()

    question_index = 0
    while f"questions[{question_index}]['id']" in data:
        question_id = data.get(f"questions[{question_index}]['id']")
        question_type = data.get(f"questions[{question_index}]['type']")
        question_text = data.get(f"questions[{question_index}]['text']")
        question_options = data.get(f"questions[{question_index}]['options']", '[]')
        question_correct_answer = data.get(f"questions[{question_index}]['correctAnswer']")
        question_file_type = data.get(f"questions[{question_index}]['fileType']")
        question_description = data.get(f"questions[{question_index}]['description']")
        uploaded_file_key = f"questions[{question_index}]['uploadedFile']"
        uploaded_file = files.get(uploaded_file_key)

        # Convert options to list from JSON string
        question_options = json.loads(question_options)
        
        # Create the question instance
        question = Question(
            test=test,
            type=question_type,
            text=question_text,
            options=question_options,
            correct_answer=int(question_correct_answer) if question_correct_answer is not None else None,
            file_type=question_file_type,
            description=question_description
        )

        # Handle the file upload if present
        if uploaded_file:
            question.uploaded_file = uploaded_file

        question.save()
        question_index += 1


    return Response({'message': 'Test created/updated successfully'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_test_details(request, test_id):
    # Retrieve the test by ID
    test = get_object_or_404(Test, id=test_id)
    # Retrieve associated questions
    questions = test.questions.all()
    
    # Prepare the response data
    response_data = {
        'title': test.title,
        'questions': []
    }
    
    for question in questions:
        question_data = {
            'id': question.id,
            'type': question.type,
            'text': question.text,
            'options': question.options,
            'correctAnswer': question.correct_answer,
            'fileType': question.file_type,
            'description': question.description,
            'uploadedFile': question.uploaded_file.url if question.uploaded_file else None
        }
        response_data['questions'].append(question_data)
    print(response_data)
    return Response(response_data)

def download_file(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        if question.uploaded_file:
            response = FileResponse(question.uploaded_file.open(), as_attachment=True)
            response['Content-Disposition'] = f'attachment; filename="{question.uploaded_file.name}"'
            return response
        else:
            raise Http404("No file associated with this question.")
    except Question.DoesNotExist:
        raise Http404("Question does not exist.")

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def add_user_test(request):
    data = request.data
    files = request.FILES
    test_id = data.get('test_id')
    test = Test.objects.get(id=test_id)
    user = request.user

    # Проверка на существование записи UserTestResult для данного пользователя и теста
    new_usertestresult, created = UserTestResult.objects.get_or_create(
        user=user, test=test,
        defaults={'status': "В обработке"}
    )

    if not created:
        # Обновляем существующий объект, если он уже есть
        new_usertestresult.status = "В обработке"
        new_usertestresult.save()

    question_index = 0
    while f"questions[{question_index}]['id']" in data:
        question_id = data.get(f"questions[{question_index}]['id']")
        question_type = data.get(f"questions[{question_index}]['type']")
        question_text = data.get(f"questions[{question_index}]['text']")
        question_options = data.get(f"questions[{question_index}]['options']", '[]')
        question_correct_answer = data.get(f"questions[{question_index}]['correctAnswer']")
        question_file_type = data.get(f"questions[{question_index}]['fileType']")
        question_description = data.get(f"questions[{question_index}]['description']")
        question_user_answer_choice = data.get(f"questions[{question_index}]['userAnswerChoice']")
        uploaded_file_key = f"questions[{question_index}]['userAnswerFile']"
        uploaded_file = files.get(uploaded_file_key)

        # Convert options to list from JSON string
        question_options = json.loads(question_options)

        question = Question.objects.get(
            test=test,
            type=question_type,
            text=question_text,
            options=question_options,
            file_type=question_file_type,
            description=question_description
        )

        if question_user_answer_choice is None:
            question_user_answer_choice = ''

        # Обновление или создание нового UserTestQuestionResult
        userquestion, created = UserTestQuestionResult.objects.update_or_create(
            user_test_result=new_usertestresult,
            question=question,
            defaults={
                'user_answer_choice': question_user_answer_choice,
            }
        )

        if uploaded_file:
            userquestion.user_answer_file = uploaded_file
            userquestion.save()
        question_index += 1

    return Response({'message': 'Test created/updated successfully'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_users_test_details(request, test_id):
    # Retrieve the test by ID
    test = Test.objects.get(id=test_id)
    user_test_results = UserTestResult.objects.filter(test=test)

    response_data = {
        'title': test.title,
        'tests': []
    }


    for user_test in user_test_results:
        user_test_questions = UserTestQuestionResult.objects.filter(user_test_result=user_test)  
        response_data_questions = {
            'test_id': user_test.test.id,
            'user_id': user_test.user.id,
            'status': user_test.status,
            'questions': []
        }
        for user_question in user_test_questions:
            user_questions_data = {
                'id': user_question.id,
                'question': user_question.question.text,
                'text': user_question.question.text,
                'options': user_question.question.options,
                'correctAnswer': user_question.question.correct_answer,
                'fileType': user_question.question.file_type,
                'description': user_question.question.description,
                'userAnswerFile': user_question.user_answer_file.url if user_question.user_answer_file else None,
                'user_answer_choice': user_question.user_answer_choice
            }
            response_data_questions['questions'].append(user_questions_data)
        response_data['tests'].append(response_data_questions)
    
    return Response(response_data)


def download_user_file(request, user_id, question_id):
    try:
        question_user_result = get_object_or_404(UserTestQuestionResult, id=question_id, user_test_result__user_id=user_id)
        
        if question_user_result.user_answer_file:
            file_path = question_user_result.user_answer_file.path
            file_name = question_user_result.user_answer_file.name
            file = open(file_path, 'rb')

            # Определение MIME-типа файла
            mime_type, _ = mimetypes.guess_type(file_path)

            # Кодирование имени файла для корректного отображения в заголовке
            encoded_file_name = urlquote(file_name)

            # Проверка, если тип файла .pdf
            if mime_type == 'application/pdf':
                response = FileResponse(file, content_type=mime_type)
                response['Content-Disposition'] = f'inline; filename="{encoded_file_name}"; filename*=UTF-8\'\'{encoded_file_name}'
            else:
                response = FileResponse(file, as_attachment=True, content_type=mime_type)
                response['Content-Disposition'] = f'attachment; filename="{encoded_file_name}"; filename*=UTF-8\'\'{encoded_file_name}'
            
            return response
        else:
            raise Http404("No file associated with this question.")
    except UserTestQuestionResult.DoesNotExist:
        raise Http404("Question does not exist.")
    except Exception as e:
        # Дополнительный блок для отладки, если возникнет другая ошибка
        print(f"Error downloading file: {e}")
        raise Http404("An error occurred while attempting to download the file.")

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_users_test_status(request):
    userTestResult = UserTestResult.objects.filter(user=request.user)
    results = []
    for i in userTestResult:
        results.append({
            'name': i.test.title,
            'status': i.status 
        })
    
    return Response({'results': results})

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_status(request):
    data = json.loads(request.body)
    user_id = data.get('userId')
    test_id = data.get('testId')
    new_status = data.get('newStatus')
    user = User.objects.get(id=user_id)
    test = Test.objects.get(id=test_id)
    usertestresult = UserTestResult.objects.get(user=user, test=test)
    usertestresult.status = new_status
    usertestresult.save()

    return Response({'message': 'Test Result updated successfully'}, status=status.HTTP_200_OK)
