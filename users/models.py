# users/models.py
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models import Q

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Кастомный пользователь с авторизацией по email."""

    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Аватар"
    )

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Доступ в админку")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # email НЕ включать — он уже USERNAME_FIELD

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Платёж пользователя. Сумма хранится в КОПЕЙКАХ (целое)."""

    PAYMENT_METHOD_CHOICES = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счёт"),
    ]
    STATUS_CHOICES = [
        ("unpaid", "Не оплачен"),
        ("paid", "Оплачен"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")

    course = models.ForeignKey(
        "lms.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Оплаченный курс",
    )
    lesson = models.ForeignKey(
        "lms.Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Оплаченный урок",
    )

    # ВНИМАНИЕ: сумма в копейках, как в Stripe (unit_amount / amount_total)
    amount = models.PositiveIntegerField(
        help_text="Сумма оплаты в копейках"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="transfer",
        verbose_name="Способ оплаты",
    )
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default="unpaid",
        verbose_name="Статус оплаты",
    )

    # Stripe
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_session_id = models.CharField(
        max_length=255, blank=True, null=True, unique=True, db_index=True
    )
    payment_url = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]
        constraints = [
            # Платёж должен относиться хотя бы к курсу ИЛИ к уроку
            models.CheckConstraint(
                condition=Q(course__isnull=False) | Q(lesson__isnull=False),
                name="payment_has_course_or_lesson",
            ),
        ]

    def __str__(self):
        return f"Платёж #{self.id} — {self.user_id} — {self.amount} коп. — {self.status}"
