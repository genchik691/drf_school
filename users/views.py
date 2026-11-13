# users/views.py
# users/views.py
from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
import stripe
from django.conf import settings

from lms.models import Course
from lms.services import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_session,
)
from .models import User, Payment
from .serializers import (
    UserProfileSerializer, PaymentSerializer,
    UserRegisterSerializer, UserListSerializer
)
from .filters import PaymentFilter

stripe.api_key = settings.STRIPE_SECRET_KEY


class RegisterAPIView(generics.CreateAPIView):
    """Регистрация — доступна анонимным."""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    """CRUD пользователей — только авторизованным."""
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class CreatePaymentView(APIView):
    """Создание платежа и ссылки на оплату через Stripe."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Создать платёж и получить ссылку на оплату',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'course_id': {'type': 'integer'},
                },
                'required': ['course_id'],
            }
        },
        responses={201: {'description': 'Ссылка на оплату'}},
    )
    def post(self, request):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {'error': 'course_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)

        try:
            # 1. Продукт в Stripe
            product = create_stripe_product(course.title)

            # 2. Цена в копейках (фиксированная, т.к. у Course нет price)
            amount = 100000  # 1000 руб. в копейках — замени на свою логику
            price = create_stripe_price(product.id, amount)

            # 3. Сессия оплаты
            success_url = request.build_absolute_uri('/payments/success/')
            cancel_url = request.build_absolute_uri('/payments/cancel/')
            session = create_stripe_session(price.id, success_url, cancel_url)

            # 4. Сохраняем платёж
            payment = Payment.objects.create(
                user=request.user,
                course=course,
                amount=amount / 100,
                payment_method='transfer',
                stripe_product_id=product.id,
                stripe_price_id=price.id,
                stripe_session_id=session.id,
                payment_url=session.url,
            )

            return Response(
                {
                    'payment_id': payment.id,
                    'payment_url': session.url,
                    'session_id': session.id,
                },
                status=status.HTTP_201_CREATED,
            )

        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = retrieve_stripe_session(session_id)
            return Response({
                'status': session.status,
                'payment_status': session.payment_status,
                'session_id': session.id,
            })
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

