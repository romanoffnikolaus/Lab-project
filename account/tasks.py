from .utils import send_activation_code
from core.celery import app
from celery import shared_task
from django.utils import timezone

from .models import User


@app.task
def send_activation_code_celery(email, activation_code):
    send_activation_code(email, activation_code)

@shared_task
def delete_activation_code(user_id):
    user = User.objects.get(id=user_id)
    if user.activation_code_created_at and timezone.now() - user.activation_code_created_at > timezone.timedelta(minutes=2):
        user.activation_code = None
        user.activation_code_created_at = None
        user.save()