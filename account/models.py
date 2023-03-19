from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from slugify import slugify
from django.utils import timezone


class UserManager(BaseUserManager):
    def _create(self, email, password, **extra_fields):
        if not email:
            raise ValueError('email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.create_activation_code()
        user.save()
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create(email, password, **extra_fields)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()


class User(AbstractUser):
    objects = UserManager()

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    experience = models.CharField(max_length=50, blank=True)
    audience = models.CharField(max_length=50, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    is_active = models.BooleanField(default=False)
    is_mentor = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    slug = models.SlugField(max_length=50, unique=True)

    activation_code = models.CharField(max_length=10, null=True)
    activation_code_created_at = models.DateTimeField(null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)

    def create_activation_code(self):
        code = get_random_string(10)
        self.activation_code = code
        self.activation_code_created_at = timezone.now()
        self.save()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    competence = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=2, blank=True)
    site_url = models.URLField(max_length=255, blank=True)
    twitter_url = models.URLField(max_length=255, blank=True)
    facebook_url = models.URLField(max_length=255, blank=True)
    linkedin_url = models.URLField(max_length=255, blank=True)
    youtube_url  = models.URLField(max_length=255, blank=True)
    image = models.ImageField(upload_to="media/", blank=True)
    is_hidden = models.BooleanField(default=False)
    is_hidden_courses = models.BooleanField(default=False)
    promotions = models.BooleanField(default=False)
    mentor_ads = models.BooleanField(default=False)
    email_ads = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username