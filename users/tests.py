# users/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User, Payment
from lms.models import Course, Lesson


class PaymentFilterTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='u1@test.ru', password='pass12345'
        )
        self.user2 = User.objects.create_user(
            email='u2@test.ru', password='pass12345'
        )
        self.course = Course.objects.create(title='Django')
        self.lesson = Lesson.objects.create(title='Урок 1', course=self.course)

        Payment.objects.create(
            user=self.user1, course=self.course,
            amount=1000, payment_method='cash'
        )
        Payment.objects.create(
            user=self.user1, lesson=self.lesson,
            amount=500, payment_method='transfer'
        )
        Payment.objects.create(
            user=self.user2, course=self.course,
            amount=2000, payment_method='cash'
        )

    def test_payments_require_auth(self):
        """Аноним не может получить платежи."""
        client = APIClient()
        response = client.get('/payments/')
        self.assertEqual(response.status_code, 401)

    def test_payments_only_own(self):
        """Пользователь видит только свои платежи."""
        client = APIClient()
        client.force_authenticate(user=self.user1)
        response = client.get('/payments/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)  # только платежи user1

    def test_filter_by_course(self):
        """Фильтр по курсу."""
        client = APIClient()
        client.force_authenticate(user=self.user1)
        response = client.get(f'/payments/?course={self.course.id}')
        self.assertEqual(len(response.data), 1)

    def test_filter_by_lesson(self):
        """Фильтр по уроку."""
        client = APIClient()
        client.force_authenticate(user=self.user1)
        response = client.get(f'/payments/?lesson={self.lesson.id}')
        self.assertEqual(len(response.data), 1)

    def test_filter_by_payment_method(self):
        """Фильтр по способу оплаты."""
        client = APIClient()
        client.force_authenticate(user=self.user1)
        response = client.get('/payments/?payment_method=cash')
        self.assertEqual(len(response.data), 1)

    def test_ordering_asc(self):
        """Сортировка по возрастанию даты."""
        client = APIClient()
        client.force_authenticate(user=self.user1)
        response = client.get('/payments/?ordering=payment_date')
        self.assertEqual(response.status_code, 200)

    def test_ordering_desc(self):
        """Сортировка по убыванию даты."""
        client = APIClient()
        client.force_authenticate(user=self.user1)
        response = client.get('/payments/?ordering=-payment_date')
        self.assertEqual(response.status_code, 200)
