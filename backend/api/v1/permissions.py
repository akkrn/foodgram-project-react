from rest_framework import permissions

from users.models import User


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == User.RoleChoice.ADMIN
            or request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.role == User.RoleChoice.ADMIN
            or request.user.is_superuser
        )
