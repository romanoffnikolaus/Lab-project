from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from .tasks import send_activation_code_celery


User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        min_length=4, required=True, write_only=True)
    
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'password_confirm',
            'is_mentor'
        )
    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        send_activation_code_celery(user.email, user.activation_code)
        return user


class MentorRegistrationSerializer(serializers.ModelSerializer):
    experience = serializers.ChoiceField(
            required=True,
            help_text='Каким видом преподавания вы занимались раньше?',
            choices=(
                ('лично, частным образом', 'лично, частным образом'),
                ('лично, профессионально', 'лично, профессионально'),
                ('онлайн', 'онлайн'),
                ('другое', 'другое'),
            )
        )
    audience = serializers.ChoiceField(
            required=True,
            help_text='Есть ли у вас аудитория, с которой вы хотите поделиться своим курсом?',
            choices=(
                ('в настоящий момент нет', 'в настоящий момент нет'),
                ('у меня маленькая аудитория', 'у меня маленькая аудитория'),
                ('у меня достаточная аудитория', 'у меня достаточная аудитория'),
            )
    )

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'is_mentor',
            'experience',
            'audience',
        )

    def update(self, validated_data):
        user = User.objects.update(**validated_data)
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
        min_length=4, required=True
    )
    new_password = serializers.CharField(
        min_length=4, required=True
    )
    new_password_confirm = serializers.CharField(
        min_length=4, required=True
    )

    class Meta:
        model = User
        fields = ('old_password', 'new_password', 'new_password_confirm')

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        new_password_confirm = attrs.pop('new_password_confirm')
        if new_password != new_password_confirm:
            raise serializers.ValidationError('Password don\'t match')
        return attrs

    def validate_old_password(self, old_password):
        user = self.context['request'].user

        if not user.check_password(old_password):
            raise serializers.ValidationError('You entered wrong password')
        return old_password

    def set_new_password(self):
        user = self.context['request'].user
        new_password = self.validated_data.get('new_password')
        user.set_password(new_password)
        user.save()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User doesn't exist")
        return email

    def send_verification_code(self):
        email = self.validated_data.get("email")
        user = User.objects.get(email=email)
        user.activation_code = get_random_string(10)
        user.save()
        send_mail(
            'Восстановление пароля',
            f'Ваш код восстановления: {user.activation_code}',
            'example@gmail.com',
            [user.email]
        )


class ForgotPasswordCompleteSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, min_length=5)
    password_confirm = serializers.CharField(required=True, min_length=5)

    def validate(self, attrs):
        email = self.context.get('email')
        activation_code = self.context.get('activation_code')
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        try:
            User.objects.get(email=email, activation_code=activation_code)
        except User.DoesNotExist:
            raise serializers.ValidationError("This user doesn't exist")

        if password != password_confirm:
            raise serializers.ValidationError("Password don't match")

        return attrs

    def set_new_password(self):
        email = self.context.get('email')
        password = self.validated_data.get("password")
        user = User.objects.filter(email=email).first()
        user.set_password(password)
        user.activation_code = ''
        user.save()