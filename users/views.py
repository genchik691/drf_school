# users/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment
from .serializers import UserProfileSerializer, PaymentSerializer
from .filters import PaymentFilter


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user


class PaymentListView(generics.ListAPIView):
    """Список платежей текущего пользователя с фильтрацией."""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]  # ✅ только авторизованные
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter

    def get_queryset(self):
        # ✅ только платежи текущего пользователя
        return Payment.objects.filter(user=self.request.user)

