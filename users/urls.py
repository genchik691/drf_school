# users/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterAPIView,
    UserViewSet,
    ProfileAPIView,
    PaymentListView,
    CreatePaymentView,
    PaymentStatusView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # JWT — открыты
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Регистрация — открыта
    path('register/', RegisterAPIView.as_view(), name='register'),

    # Закрыто
    path('users/profile/', ProfileAPIView.as_view(), name='user-profile'),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('payments/create/', CreatePaymentView.as_view(), name='payment-create'),
    path('payments/status/<str:session_id>/', PaymentStatusView.as_view(), name='payment-status'),
] + router.urls

