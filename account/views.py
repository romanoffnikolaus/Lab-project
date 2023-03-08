from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema

from . import serializers
from . import models


User = get_user_model()

class RegistrationView(generics.CreateAPIView):
    serializer_class = serializers.RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        is_mentor = serializer.validated_data.get('is_mentor')

        if is_mentor:
            mentor_serializer = serializers.MentorRegistrationSerializer(data=request.data)
            mentor_serializer.is_valid(raise_exception=True)
            mentor_serializer.save()
            return Response({'message': 'Аккаунт ментора успешно создан. Ожидайте письма с подтверждением регистрации'}, status=200)
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


class ChangePasswordView(APIView):
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


class ForgotPasswordView(APIView):
    @swagger_auto_schema(request_body=serializers.ForgotPasswordSerializer)
    def post(self, request):
        serializer = serializers.ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.send_verification_email()
            return Response('Вам выслали сообщение для восстановления пароля')


class ForgotPasswordCompleteView(APIView):
    @swagger_auto_schema(request_body=serializers.ForgotPasswordCompleteSerializer)
    def post(self, request):
        serializer = serializers.ForgotPasswordCompleteSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response(
                'Ваш пароль успешно восстановлен'
            )


class ProfileView(ModelViewSet):
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
