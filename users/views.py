# users/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment
from .serializers import UserProfileSerializer, PaymentSerializer
from .filters import PaymentFilter


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля текущего пользователя."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user


class PaymentListView(generics.ListAPIView):
    """Список платежей с фильтрацией и сортировкой."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]  # по заданию безопасность не нужна
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter

