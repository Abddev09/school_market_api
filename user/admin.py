from django.contrib import admin

from user.models import User



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username","first_name","last_name", "ball","is_staff","is_superuser","role"]
    list_filter = ["role", "is_staff"]
    search_fields = ["username", "first_name", "last_name", "ball"]
    ordering = ["-ball"]