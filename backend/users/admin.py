from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "email", "first_name", "last_name"]
    search_fields = ["username", "email"]


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ["user", "author"]
    search_fields = ["user__username", "author__username"]

    def get_queryset(self, request: admin.ModelAdmin) -> Follow:
        qs = super().get_queryset(request)
        return qs.select_related("user", "author")
