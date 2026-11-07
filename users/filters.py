# users/filters.py
import django_filters
from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    """Фильтр для платежей."""
    course = django_filters.NumberFilter(field_name='course__id')
    lesson = django_filters.NumberFilter(field_name='lesson__id')
    payment_method = django_filters.ChoiceFilter(choices=Payment.PAYMENT_METHOD_CHOICES)
    ordering = django_filters.OrderingFilter(
        fields=(
            ('payment_date', 'payment_date'),
        ),
    )

    class Meta:
        model = Payment
        fields = ['course', 'lesson', 'payment_method']
