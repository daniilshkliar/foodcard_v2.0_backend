from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from phonenumber_field.validators import validate_international_phonenumber

from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'first_name', 'last_name', 'is_staff']

    def get_is_staff(self, obj):
        return obj.groups.filter(name='Staff').exists()


class SignupSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone', 'first_name', 'last_name', 'password1', 'password2']

    def validate(self, data):
        password1 = data.pop('password1')
        password2 = data.pop('password2')
        if password1 and password2 and password1 != password2:
            raise serializers.ValidationError("Passwords don't match")
        data['password'] = password1
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        try:
            validate_email(identifier)
            user = User.objects.filter(email=identifier, is_active=True).first()
        except ValidationError:
            try:
                validate_international_phonenumber(identifier)
                user = User.objects.filter(phone=identifier, is_active=True).first()
            except ValidationError:
                raise serializers.ValidationError('You have not entered an email address or phone number')

        if not user or not user.check_password(password):
            raise serializers.ValidationError('No active account found with the given credentials')

        tokens = RefreshToken.for_user(user)
        data['access'] = tokens.access_token
        data['refresh'] = tokens
        return data