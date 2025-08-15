from rest_framework import serializers
from accounts.models import CustomUserModel, ProfileUserModel
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterUserSerializers(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
        'username': {
            'validators': []
        }
    }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        if len(value) < 6:
            raise serializers.ValidationError('Username must be at least 6 characters long.')
        if not value.isalnum():
            raise serializers.ValidationError("Username can only contain letters and numbers.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        if not (value.endswith('@gmail.com') or value.endswith('@yahoo.com')):
            raise serializers.ValidationError('Email must be a Gmail or Yahoo address.')
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not any(char in '!@#$%^&*()_+' for char in value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate(self, value):
        username = value.get('username')
        password = value.get('password')
        email = value.get('email')

        if username == password:
            raise serializers.ValidationError("Username and password cannot be the same.")
        if email and email in password:
            raise serializers.ValidationError("Password cannot contain the email address.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        CustomUserModel.objects.create(user=user)
        ProfileUserModel.objects.create(user=user)
        return user