from django.shortcuts import render
from accounts.models import CustomUserModel
from accounts.serializers import RegisterUserSerializers
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
# Create your views here.

User = get_user_model()

class RegisterUserView(viewsets.ModelViewSet):

    permission_classes = [AllowAny]

    queryset = User.objects.all()
    serializer_class = RegisterUserSerializers


class SetTelegramIDView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get("telegram_id")
        tel_username = request.data.get("tel_username")

        if not telegram_id:
            return Response({"status": "missing telegram_id"}, status=400)

        obj, created = CustomUserModel.objects.get_or_create(user=request.user)
        obj.telegram_id = telegram_id
        if tel_username:
            obj.tel_username = tel_username
        obj.save()

        return Response({"status": "ok"})