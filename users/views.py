# users/views.py
from decimal import Decimal

import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course
from lms.services import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_session,
    retrieve_stripe_session,
)
from .filters import PaymentFilter
from .models import Payment, User
from .serializers import (
    PaymentSerializer,
    UserListSerializer,
    UserProfileSerializer,
    UserRegisterSerializer,
)

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
    ordering = ["-payment_date"]          # ← исправлено: поле модели — payment_date

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class CreatePaymentView(APIView):
    """Создание платежа и ссылки на оплату через Stripe."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Создать платёж и получить ссылку на оплату",
        request={
            "application/json": {
                "type": "object",
                "properties": {"course_id": {"type": "integer"}},
                "required": ["course_id"],
            }
        },
        responses={
            201: OpenApiResponse(description="Ссылка на оплату"),
            400: OpenApiResponse(description="Ошибка валидации или Stripe"),
            404: OpenApiResponse(description="Курс не найден"),
        },
    )
    def post(self, request):
        course_id = request.data.get("course_id")
        if not course_id:
            return Response(
                {"error": "course_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = get_object_or_404(Course, id=course_id)

        # Цена из модели курса, в копейках (целое).
        # Course.price — Decimal в рублях.
        amount_kopecks = int(Decimal(course.price) * 100)
        if amount_kopecks <= 0:
            return Response(
                {"error": "У курса не задана корректная цена"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = create_stripe_product(course.title)
            price = create_stripe_price(product.id, amount_kopecks)

            success_url = request.build_absolute_uri("/payments/success/")
            cancel_url = request.build_absolute_uri("/payments/cancel/")
            session = create_stripe_session(price.id, success_url, cancel_url)

            payment = Payment.objects.create(
                user=request.user,
                course=course,
                amount=amount_kopecks,
                payment_method="transfer",
                stripe_product_id=product.id,
                stripe_price_id=price.id,
                stripe_session_id=session.id,
                payment_url=session.url,
            )

            return Response(
                {
                    "payment_id": payment.id,
                    "payment_url": session.url,
                    "session_id": session.id,
                },
                status=status.HTTP_201_CREATED,
            )

        except stripe.error.StripeError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaymentStatusView(APIView):
    """Проверка статуса платежа с синхронизацией в БД."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Проверить статус платежа Stripe",
        responses={
            200: OpenApiResponse(description="Статус платежа"),
            400: OpenApiResponse(description="Ошибка Stripe"),
            404: OpenApiResponse(description="Платёж не найден"),
        },
    )
    def get(self, request, session_id):
        payment = get_object_or_404(
            Payment, stripe_session_id=session_id, user=request.user
        )

        try:
            session = retrieve_stripe_session(session_id)
        except stripe.error.StripeError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = "paid" if session.payment_status == "paid" else "unpaid"
        if payment.status != new_status:
            payment.status = new_status
            payment.save(update_fields=["status"])

        return Response(
            {
                "stripe_status": session.status,           # open/complete/expired
                "payment_status": session.payment_status,  # paid/unpaid
                "session_id": session.id,
                "amount_total": session.amount_total,      # в копейках
            },
            status=status.HTTP_200_OK,
        )


class PaymentSuccessView(APIView):
    """Страница успешного завершения оплаты (редирект Stripe)."""
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Успешное завершение оплаты",
        responses={200: OpenApiResponse(description="Оплата прошла успешно")},
    )
    def get(self, request):
        return Response(
            {"status": "success", "message": "Оплата прошла успешно"},
            status=status.HTTP_200_OK,
        )


class PaymentCancelView(APIView):
    """Страница отмены оплаты (редирект Stripe)."""
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Отмена оплаты",
        responses={200: OpenApiResponse(description="Оплата отменена")},
    )
    def get(self, request):
        return Response(
            {"status": "cancelled", "message": "Оплата отменена"},
            status=status.HTTP_200_OK,
        )
