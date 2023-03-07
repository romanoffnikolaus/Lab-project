from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from . import serializers
from .utils import send_activation_code


User = get_user_model()

class RegistrationView(generics.CreateAPIView):
    serializer_class = serializers.RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_mentor = serializer.validated_data.get('is_mentor')
        if is_mentor:
            serializer = serializers.MentorRegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            email = serializer.validated_data.get("email")
            user = User.objects.get(email=email)
            send_activation_code(user.email, user.activation_code)
            return Response(serializer.data)
        super().post(request, *args, **kwargs)
        return Response(serializer.data)


class ActivationView(APIView):
    def get(self, request, email, activation_code):
        user = User.objects.filter(
            email=email,
            activation_code=activation_code).first()
        if not user:
            return Response('User not found', status=400)
        user.activation_code = ''
        user.is_active = True
        user.save()
        return Response('Account is activated', status=200)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = serializers.ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            message = 'You successfully changed your password'
        else:
            message = 'You entered wrong password'
        return Response(message)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = serializers.ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.send_verification_code()
            return Response("We've sent you activation code to your email")


class ForgotPasswordCompleteView(APIView):
    def post(self, request, email, activation_code):
        context = {'email': email, "activation_code": activation_code}
        serializer = serializers.ForgotPasswordCompleteSerializer(
            data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response('Your password succesfully changed')
