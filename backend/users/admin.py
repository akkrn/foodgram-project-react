from django.contrib import admin
from .models import User, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'first_name', 'last_name']
    search_fields = ['username', 'email']
    list_filter = ['username', 'email']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['user', 'author']
    search_fields = ['user__username', 'author__username']