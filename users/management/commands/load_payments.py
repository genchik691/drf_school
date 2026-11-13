# users/management/commands/load_payments.py
from django.core.management.base import BaseCommand
from users.models import User, Payment
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Загружает тестовые платежи'

    def handle(self, *args, **options):
        user = User.objects.first()
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        if not user:
            self.stdout.write(self.style.ERROR('Нет пользователей'))
            return

        Payment.objects.get_or_create(
            user=user, course=course, lesson=None,
            defaults={'amount': 15000, 'payment_method': 'transfer'}
        )
        Payment.objects.get_or_create(
            user=user, course=None, lesson=lesson,
            defaults={'amount': 3000, 'payment_method': 'cash'}
        )
        self.stdout.write(self.style.SUCCESS('✅ Платежи загружены'))
