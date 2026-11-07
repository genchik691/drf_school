# users/urls.py
from django.urls import path
from .views import ProfileAPIView

urlpatterns = [
    path('users/profile/', ProfileAPIView.as_view(), name='user-profile'),
]
