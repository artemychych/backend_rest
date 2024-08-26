from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import json
from ...models import *
from collections import Counter
import time
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.core.cache import cache

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_skills(request):
    skills = Skill.objects.all()
    internship_skills = SkillInternship.objects.filter(internship=request.user)
    array_skills = []
    for i in internship_skills:
        array_skills.append(i.skill.name)
    user_checked_skills = []
    for i in skills:
        if i.name in array_skills:
            user_checked_skills.append({'name': i.name, 'checked': True})
        else:
            user_checked_skills.append({'name': i.name, 'checked': False})
    return Response({'skills': user_checked_skills})

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_internship(request):
    print(request.body)
    data = json.loads(request.body)
    submitted_skills = data.get('skills')
    name = data.get('name')
    date_start = data.get('date_start')
    date_end_selection = data.get('date_end_selection')
    description = data.get('description')
    company = User.objects.get(id=request.user.id)

    internship = Internship.objects.create(name=name, description=description, 
                                           company=company, date_start=date_start, date_end_selection=date_end_selection)
    for skill in submitted_skills:
        skill_temp = Skill.objects.get(name=skill)
        skill_internship = SkillInternship.objects.create(internship=internship, skill=skill_temp)
    return Response({'message': 'Internship created successfully'})

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_internship_skills(request):
    data = json.loads(request.body)
    internship_id = data.get('id')
    submitted_skills = data.get('skills')

    # Находим стажировку по id
    internship = get_object_or_404(Internship, id=internship_id)

    # Получаем все существующие навыки для этой стажировки
    existing_skills = SkillInternship.objects.filter(internship=internship)

    # Создаем список навыков для удаления
    skills_to_delete = []
    for existing_skill in existing_skills:
        if existing_skill.skill.name not in submitted_skills:
            skills_to_delete.append(existing_skill.id)

    # Удаляем навыки, которых нет в списке submitted_skills
    SkillInternship.objects.filter(id__in=skills_to_delete).delete()

    # Добавляем новые навыки
    for skill_name in submitted_skills:
        # Проверяем, существует ли такой навык
        try:
            skill = Skill.objects.get(name=skill_name)
        except Skill.DoesNotExist:
            return Response({'error': f"Навык '{skill_name}' не найден."}, status=400)

        # Проверяем, существует ли уже связь между стажировкой и навыком
        if not SkillInternship.objects.filter(internship=internship, skill=skill).exists():
            # Если связи нет, создаем ее
            SkillInternship.objects.create(internship=internship, skill=skill)

    return Response({'message': 'Навыки стажировки успешно обновлены.'})


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_internships(request):
    start_time = time.time()
    
    # Попробовать получить данные из кеша
    cache_key = f'internships_user_{request.user.id}'
    sorted_internships = cache.get(cache_key)

    if not sorted_internships:
        # Данные отсутствуют в кеше, получаем их из базы данных
        internships = Internship.objects.prefetch_related(
            Prefetch(
                'skillinternship_set', 
                queryset=SkillInternship.objects.select_related('skill')
            )
        ).select_related('company')

        internships_json = [
            {
                'id': internship.id,
                'name': internship.name,
                'description': internship.description,
                'date_start': internship.date_start,
                'date_end_selection': internship.date_end_selection,
                'skills': [si.skill.name for si in internship.skillinternship_set.all()],
                'created_at': internship.created_at
            }
            for internship in internships
        ]

        user_skills = set(SkillUser.objects.filter(user=request.user).values_list('skill__name', flat=True))

        if not user_skills:
            sorted_internships = sorted(
                internships_json,
                key=lambda internship: internship['created_at'],
                reverse=True
            )
        else:
            sorted_internships = sorted(
                internships_json,
                key=lambda internship: (
                    len(set(internship['skills']) & user_skills) == 0,
                    -len(set(internship['skills']) & user_skills),
                    len(internship['skills']),
                    internship['created_at']
                )
            )
        
       
    
    end_time = time.time()
    print("Время выполнения:", end_time - start_time)
    return Response({'internships': sorted_internships})

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])    
def get_company_internships_ids(request):
    internships = Internship.objects.filter(company=request.user)
    intern_formatted = []
    for internship in internships:
        intern_formatted.append(internship.id)
    return Response({'internships': intern_formatted})

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user(request):
    user_groups = request.user.groups.all()
    group = None
    for i in user_groups:
        group = i 
        break
    user = User.objects.get(id=request.user.id)
    return Response({'username': user.username, 'email': user.email, 'group': str(group)})

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def save_skills(request):
    data = json.loads(request.body)
    submitted_skills = set(data.get('skills', []))
    user_skills = SkillUser.objects.filter(user=request.user)
    existing_skills = set(user_skill.skill.name for user_skill in user_skills)
    skills_to_delete = existing_skills - submitted_skills
    user_skills.filter(skill__name__in=skills_to_delete).delete()
    skills_to_add = submitted_skills - existing_skills
    new_skill_users = []
    for skill_name in skills_to_add:
        skill = Skill.objects.get_or_create(name=skill_name)[0]
        new_skill_users.append(SkillUser(user=request.user, skill=skill))
    SkillUser.objects.bulk_create(new_skill_users) 

    return Response({'message': 'Навыки успешно обновлены пользователю'})

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_internship(request, internship_id):
    internship = Internship.objects.get(id=internship_id)
    internship_json = {
            'id': internship.id,
            'name': internship.name,
            'description': internship.description,
            'date_start': internship.date_start,
            'date_end_selection': internship.date_end_selection,
            'skills': [si.skill.name for si in internship.skillinternship_set.all()],
            'created_at': internship.created_at
        }
    return Response({'internship': internship_json})
        
    