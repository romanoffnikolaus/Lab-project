# Generated by Django 4.1.7 on 2023-03-19 09:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "account",
            "0007_rename_activation_code_expiration_user_activation_code_created_at",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="activation_code_created_at",
        ),
    ]