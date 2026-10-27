import re
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with field validation,
    duplicate check, and password strength verification.
    """
    email = serializers.EmailField(
        required=True,
        max_length=255,
        help_text="Valid and unique email address."
    )
    name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="User's full name."
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Password must satisfy security complexity standards."
    )

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password']
        read_only_fields = ['id']

    def validate_name(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Name field cannot be blank.")
        return stripped

    def validate_email(self, value):
        normalized = value.strip().lower()
        if not normalized:
            raise serializers.ValidationError("Email field cannot be blank.")
        if User.objects.filter(email=normalized).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized

    def validate_password(self, value):
        if not value or len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        # Django built-in password validation checks
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

        return value

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )


class UserResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for safe user representations excluding sensitive attributes.
    """
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'date_joined']
        read_only_fields = ['id', 'name', 'email', 'date_joined']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer to customize token payload and response format.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['name'] = user.name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'name': self.user.name,
            'email': self.user.email
        }
        return data
