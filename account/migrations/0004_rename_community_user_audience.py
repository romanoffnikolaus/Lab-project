# Generated by Django 4.1.7 on 2023-03-08 06:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0003_rename_audience_user_community_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="community",
            new_name="audience",
        ),
    ]
