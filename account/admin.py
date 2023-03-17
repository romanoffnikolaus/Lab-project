from django.contrib import admin

from .models import User, Profile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_active", "is_mentor")

@admin.register(Profile)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user',)