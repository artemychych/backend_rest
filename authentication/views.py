from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import UserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from .models import *
from .serializers import GroupSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    groups = user.groups.all()
    for group in groups:
        print(group)

    if not user.check_password(request.data['password']):
        return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"token": token.key, "user": serializer.data})

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        group = Group.objects.get(name='candidates')
        user.groups.add(group)
        user.save()
        token = Token.objects.create(user=user)
        print(user.groups)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def signup_companies(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        group = Group.objects.get(name='companies')
        user.groups.add(group)
        user.save()
        token = Token.objects.create(user=user)
        print(user.groups)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({f"passed for {request.user.email}"})

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
def get_companies(request):
    group = Group.objects.get(name='companies')
    users_in_companies_group = User.objects.filter(groups__name='companies')
    companies_json = []
    # Если нужно, можно обработать пользователей дальше
    for user in users_in_companies_group:
        companies_json.append({
            'id': user.id, # type: ignore
            'name': user.username,
            'email': user.email
        })
    return Response({"companies": companies_json})


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, user_id):
    user = User.objects.get(id=user_id)
    return Response({"name": user.username, "email": user.email})

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_internships_by_company_id(request, company_id):
    company = User.objects.get(id=company_id)
    internships = Internship.objects.filter(company=company)
    internships_json = []
    for i in internships:
        internships_json.append({
            'id': i.id, # type: ignore
            'name': i.name,
            'description': i.description
        })
    return Response({"internships": internships_json})
