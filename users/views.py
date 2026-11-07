# users/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserProfileSerializer


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля текущего пользователя."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user
