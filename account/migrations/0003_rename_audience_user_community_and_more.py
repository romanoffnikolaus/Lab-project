# Generated by Django 4.1.7 on 2023-03-07 11:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0002_alter_user_activation_code"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="audience",
            new_name="community",
        ),
        migrations.AlterField(
            model_name="user",
            name="activation_code",
            field=models.CharField(max_length=10, null=True),
        ),
    ]
