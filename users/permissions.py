# users/permissions.py
from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Доступ только модераторам."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name='Модераторы').exists()
        )


class IsOwnerOrModerator(BasePermission):
    """Доступ владельцу объекта или модератору."""

    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='Модераторы').exists():
            return True
        return obj.owner == request.user
