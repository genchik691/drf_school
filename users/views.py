from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import User
from .serializers import UserProfileSerializer


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля пользователя."""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]  # ✅ открыто по заданию
    