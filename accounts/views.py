from smtplib import SMTPAuthenticationError

from django.conf import settings
from rest_framework.response import Response
from django.utils.encoding import force_bytes
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.decorators import api_view, permission_classes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from guardian.shortcuts import get_perms

from .models import User
from .serializers import *
from core.models import Place


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def retrieve(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def permissions(self, request, pk=None):
        try:
            place = Place.objects.get(id=pk)
            perms = {'permissions': get_perms(request.user, place)}
            return Response(perms, status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save(is_active=False)

    try:
        activation_token = PasswordResetTokenGenerator()
        message = f"""
            Hi {user.first_name}.
            Please click on the link below to confirm your registration:
            {settings.CORS_ORIGIN_WHITELIST[0]}/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{activation_token.make_token(user)}/
        """
        user.email_user('Activate your FOODCARD account', message, settings.EMAIL_HOST_USER)
    except SMTPAuthenticationError as exc:
        return Response({"message" : exc.smtp_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.AllowAny,])
def activate_account(request, uidb64, utoken):
    try:
        user_id = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=user_id)
    except (TypeError, ValueError):
        user = None
        
    if PasswordResetTokenGenerator().check_token(user, utoken):
        user.is_active = True
        user.save()
        tokens = RefreshToken.for_user(user)
        access_max_age = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        refresh_max_age = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        response = Response()
        response.set_cookie(key=settings.ACCESS_COOKIE_NAME, value=tokens.access_token, httponly=True, max_age=access_max_age)
        response.set_cookie(key=settings.REFRESH_COOKIE_NAME, value=tokens, httponly=True, max_age=refresh_max_age)
        return response
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    access_max_age = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
    refresh_max_age = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
    response = Response()
    response.set_cookie(key=settings.ACCESS_COOKIE_NAME, value=serializer.data['access'], httponly=True, max_age=access_max_age)
    response.set_cookie(key=settings.REFRESH_COOKIE_NAME, value=serializer.data['refresh'], httponly=True, max_age=refresh_max_age)
    return response


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated,])
def logout(request):
    response = Response()
    response.delete_cookie(settings.ACCESS_COOKIE_NAME)
    response.delete_cookie(settings.REFRESH_COOKIE_NAME)
    return response


@api_view(['GET'])
@permission_classes([permissions.AllowAny,])
def refresh(request):
    if refresh_token := request.COOKIES.get('refresh'):
        if tokens := RefreshToken(refresh_token):
            tokens.set_jti()
            tokens.set_exp()
            access_max_age = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
            refresh_max_age = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
            response = Response()
            response.set_cookie(key=settings.ACCESS_COOKIE_NAME, value=tokens.access_token, httponly=True, max_age=access_max_age)
            response.set_cookie(key=settings.REFRESH_COOKIE_NAME, value=tokens, httponly=True, max_age=refresh_max_age)
            return response
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)