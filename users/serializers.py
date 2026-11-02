from rest_framework import serializers
from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar']
        read_only_fields = ['id', 'email']
