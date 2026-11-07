# users/serializers.py
from rest_framework import serializers
from .models import User, Payment


# ✅ Сначала PaymentSerializer
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'payment_date', 'course', 'lesson', 'amount', 'payment_method']
        read_only_fields = ['id', 'payment_date']


# ✅ Потом UserProfileSerializer (использует PaymentSerializer)
class UserProfileSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'payments']
        read_only_fields = ['id', 'email', 'payments']
