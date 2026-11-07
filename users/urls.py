# users/urls.py
from django.urls import path
from .views import ProfileAPIView, PaymentListView

urlpatterns = [
    path('users/profile/', ProfileAPIView.as_view(), name='user-profile'),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
]
