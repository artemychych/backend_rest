from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import json

from ...models import *

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_group(request):
    user_groups = request.user.groups.all()
    group = None
    for i in user_groups:
        group = i 
        break
    return Response({"group": group})

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_skills(request):
    skills = Skill.objects.all()
    user_skills = SkillUser.objects.filter(user=request.user)
    array_skills = []
    for i in user_skills:
        array_skills.append(i.skill.name)
    user_checked_skills = []
    for i in skills:
        if i.name in array_skills:
            user_checked_skills.append({'name': i.name, 'checked': True})
        else:
            user_checked_skills.append({'name': i.name, 'checked': False})
    return Response({'skills': user_checked_skills})

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





