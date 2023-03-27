from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from . import serializers
from . import models
from .permissions import IsOwnerOrReadOnly


User = get_user_model()

class PermissionMixin:
    permission_classes = [IsAuthenticated]



class RegistrationView(generics.CreateAPIView):
    serializer_class = serializers.RegistrationSerializer

    def post(self, request, *args, **kwargs):
        is_mentor = request.data.get('is_mentor')
        if is_mentor:
            serializer = serializers.MentorRegistrationSerializer(data=request.data)
        else:
            serializer = serializers.RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Аккаунт успешно создан. Ожидайте письма с подтверждением регистрации'}, status=200)


class ActivationView(APIView):
    def get(self, request, email, activation_code):
        user = User.objects.filter(
            email=email,
            activation_code=activation_code).first()
        if not user:
            return Response('Пользователь не найден', status=400)
        user.activation_code = ''
        user.is_active = True
        user.save()
        return Response('Активирован', status=200)


class ChangePasswordView(PermissionMixin, APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=serializers.ChangePasswordSerializer)
    def post(self, request):
        serializer = serializers.ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            message = 'Смена пароля прошла успешно'
        else:
            message = 'Введен некорректный пароль'
        return Response(message)


class ForgotPasswordView(PermissionMixin, APIView):
    @swagger_auto_schema(request_body=serializers.ForgotPasswordSerializer)
    def post(self, request):
        serializer = serializers.ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.send_verification_email()
            return Response('Вам выслали сообщение для восстановления пароля')


class ForgotPasswordCompleteView(PermissionMixin, APIView):
    @swagger_auto_schema(request_body=serializers.ForgotPasswordCompleteSerializer)
    def post(self, request):
        serializer = serializers.ForgotPasswordCompleteSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response(
                'Ваш пароль успешно восстановлен'
            )


class APILogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if self.request.data.get('all'):
            token: OutstandingToken
            for token in OutstandingToken.objects.filter(user=request.user):
                _, _ = BlacklistedToken.objects.get_or_create(token=token)
            return Response("Refresh token in backlist")
        refresh_token = self.request.data.get('refresh_token')
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        return Response('Всего доброго!')


class ProfileView(ModelViewSet):
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
