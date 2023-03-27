from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .tasks import send_activation_code_celery
from .models import Profile
from .tasks import delete_activation_code
from django.utils import timezone


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        min_length=4, required=True, write_only=True)
    first_name = serializers.CharField(
        max_length=30, required=True)
    last_name = serializers.CharField(
        max_length=30, required=True)
    
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
        send_activation_code_celery.delay(user.email, user.activation_code)
        return user


class MentorRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        min_length=4, required=True, write_only=True)
    experience = serializers.ChoiceField(
            required=True,
            help_text='Каким видом преподавания вы занимались раньше?',
            choices=(
                ('Лично, частным образом', 'Лично, частным образом'),
                ('Лично, профессионально', 'Лично, профессионально'),
                ('Онлайн', 'Онлайн'),
                ('Другое', 'Другое'),
            )
        )
    audience = serializers.ChoiceField(required=True,
            help_text='Есть ли у вас аудитория, с которой вы хотите поделиться своим курсом?',
            choices=(
                ('В настоящий момент нет', 'В настоящий момент нет'),
                ('У меня маленькая аудитория', 'У меня маленькая аудитория'),
                ('У меня достаточная аудитория', 'У меня достаточная аудитория'),
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
            'password_confirm',
            'is_mentor',
            'experience',
            'audience'
        )
    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def create(self, validated_data):
        user_data = {
            'username': self.context.get('username'),
            'first_name': self.context.get('first_name'),
            'last_name': self.context.get('last_name'),
            'email': self.context.get('email'),
            'password': self.context.get('password'),
            'is_mentor': True
        }
        user_data.update(validated_data)
        user = User.objects.create_user(**user_data)
        send_activation_code_celery.delay(user.email, user.activation_code)
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    
    old_password = serializers.CharField(min_length=4, required=True)
    new_password = serializers.CharField(min_length=4, required=True)
    new_password_confirm = serializers.CharField(min_length=4, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'new_password', 'new_password_confirm')

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        new_password_confirm = attrs.pop('new_password_confirm')
        if new_password != new_password_confirm:
            raise serializers.ValidationError('Пароли не совпадают!')
        return attrs

    def validate_old_password(self, old_password):
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError('Введен некорректный пароль')
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
            raise serializers.ValidationError("Пользователь с такими данными не найден")
        return email

    def send_verification_email(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.create_activation_code()
        user.activation_code_created_at = timezone.now()
        user.save()
        delete_activation_code.apply_async(args=[user.id], countdown=120)
        send_mail(
            'Восстановление пароля',
            f'Ваш код восстановления: {user.activation_code}',
            'example@gmail.com',
            [user.email]
        )


class ForgotPasswordCompleteSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=4, required=True)
    password_confirm = serializers.CharField(min_length=4, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        password1 = attrs.get('password')
        password2 = attrs.get('password_confirm')
        if not User.objects.filter(email=email, activation_code=code).exists():
            raise serializers.ValidationError('Пользователь не найден или введен неправильный код')
        if password1 != password2:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def set_new_password(self):
        email = self.validated_data.get('email')
        password = self.validated_data.get('password')
        user = User.objects.get(email=email)
        user.set_password(password)
        user.activation_code = ''
        user.save()


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    language = serializers.ChoiceField(
            required=True,
            help_text='Выберете Ваш основной язык',
            choices=(
                ('Ru', 'Ru'),
                ('En', 'En'),
                ('Kg', 'Kg')
            )
        )
    
    class Meta:
        model = Profile
        fields = '__all__'
    
    def create(self,validated_data):
        request = self.context.get('request')
        user = request.user
        profile = Profile.objects.create(user=user, **validated_data)
        return profile

    def validate_site_url(self, website_url):
        if not website_url.startswith('https://'):
            raise serializers.ValidationError(
                'Введен некорректный адрес вебсайта. Ссылка должна начинаться с "www." или "https://"')
        return website_url

    def validate_twitter_url(self, twitter_url):
        if not twitter_url.startswith('https://twitter.com/'):
            raise serializers.ValidationError('Введенна некорректная ссылка на профиль в твиттер. Пример: "https://twitter.com/Krutoy"')
        return twitter_url
    
    def validate_facebook_url(self, facebook_url):
        if not facebook_url.startswith('https://www.facebook.com/'):
            raise serializers.ValidationError('Введена некорректная ссылка на facebook. Пример: "https://www.facebook.com/Krutoy"')
        return facebook_url
    
    def validate_youtube_url(self, youtube_url):
        if not youtube_url.startswith('https://www.youtube.com/@'):
            raise serializers.ValidationError('Введенна некорректная ссылка на ютуб канал. Пример: "https://www.youtube.com/@Krutoy"')
        return youtube_url
    
    def validate_linkedin_url(self, linkedin_url):
        if not linkedin_url.startswith('https://www.linkedin.com/'):
            raise serializers.ValidationError('Введенна некорректная ссылка на Linked_in. Пример: "https://www.linkedin.com/in/Krutoy"')
        return linkedin_url
    