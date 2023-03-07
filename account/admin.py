from django.contrib import admin

from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_active", "is_mentor", "first_name", "last_name")
    list_editable = ("is_active", "is_mentor")
    search_fields = ("username", "email", "first_name", "last_name")