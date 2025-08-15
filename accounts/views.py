from django.shortcuts import render
from accounts.models import CustomUserModel
from accounts.serializers import RegisterUserSerializers
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
# Create your views here.

User = get_user_model()

class RegisterUserView(viewsets.ModelViewSet):

    permission_classes = [AllowAny]

    queryset = User.objects.all()
    serializer_class = RegisterUserSerializers