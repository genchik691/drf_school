from django.urls import path
from .views import ProfileAPIView

urlpatterns = [
    path('users/<int:pk>/', ProfileAPIView.as_view(), name='user-profile'),
]
