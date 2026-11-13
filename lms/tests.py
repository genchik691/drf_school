# lms/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from lms.models import Course, Lesson


class PermissionsTest(TestCase):
    """Проверка составных permissions на чистой установке."""

    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@test.ru', password='pass12345'
        )
        self.other = User.objects.create_user(
            email='other@test.ru', password='pass12345'
        )
        self.moderator = User.objects.create_user(
            email='moder@test.ru', password='pass12345'
        )
        moderator_group, _ = self.moderator.groups.get_or_create(name='Модераторы')

        self.course = Course.objects.create(title='Django', owner=self.owner)
        self.lesson = Lesson.objects.create(
            title='Урок 1', course=self.course, owner=self.owner
        )

    # ===== Курсы =====
    def test_owner_can_create_course(self):
        client = APIClient()
        client.force_authenticate(user=self.owner)
        response = client.post('/courses/', {'title': 'Новый'})
        self.assertEqual(response.status_code, 201)

    def test_other_can_create_course(self):
        """Другой пользователь (не модератор) тоже может создавать."""
        client = APIClient()
        client.force_authenticate(user=self.other)
        response = client.post('/courses/', {'title': 'Новый'})
        self.assertEqual(response.status_code, 201)

    def test_moderator_cannot_create_course(self):
        client = APIClient()
        client.force_authenticate(user=self.moderator)
        response = client.post('/courses/', {'title': 'Модераторский'})
        self.assertEqual(response.status_code, 403)

    def test_owner_can_update_course(self):
        client = APIClient()
        client.force_authenticate(user=self.owner)
        response = client.patch(f'/courses/{self.course.id}/', {'title': 'Обновлён'})
        self.assertEqual(response.status_code, 200)

    def test_moderator_can_update_course(self):
        client = APIClient()
        client.force_authenticate(user=self.moderator)
        response = client.patch(f'/courses/{self.course.id}/', {'title': 'Модер'})
        self.assertEqual(response.status_code, 200)

    def test_other_cannot_update_course(self):
        client = APIClient()
        client.force_authenticate(user=self.other)
        response = client.patch(f'/courses/{self.course.id}/', {'title': 'Хак'})
        self.assertEqual(response.status_code, 404)

    def test_owner_can_delete_course(self):
        client = APIClient()
        client.force_authenticate(user=self.owner)
        response = client.delete(f'/courses/{self.course.id}/')
        self.assertEqual(response.status_code, 204)

    def test_moderator_cannot_delete_course(self):
        client = APIClient()
        client.force_authenticate(user=self.moderator)
        response = client.delete(f'/courses/{self.course.id}/')
        self.assertEqual(response.status_code, 403)

    def test_other_cannot_delete_course(self):
        client = APIClient()
        client.force_authenticate(user=self.other)
        response = client.delete(f'/courses/{self.course.id}/')
        self.assertEqual(response.status_code, 404)

    # ===== Уроки =====
    def test_owner_can_create_lesson(self):
        client = APIClient()
        client.force_authenticate(user=self.owner)
        response = client.post('/lessons/', {
            'title': 'Урок 2', 'course': self.course.id
        })
        self.assertEqual(response.status_code, 201)

    def test_moderator_cannot_create_lesson(self):
        client = APIClient()
        client.force_authenticate(user=self.moderator)
        response = client.post('/lessons/', {
            'title': 'Модерский', 'course': self.course.id
        })
        self.assertEqual(response.status_code, 403)

    def test_moderator_can_update_lesson(self):
        client = APIClient()
        client.force_authenticate(user=self.moderator)
        response = client.patch(f'/lessons/{self.lesson.id}/', {'title': 'Модер'})
        self.assertEqual(response.status_code, 200)

    def test_moderator_cannot_delete_lesson(self):
        client = APIClient()
        client.force_authenticate(user=self.moderator)
        response = client.delete(f'/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, 403)

    def test_other_cannot_update_lesson(self):
        client = APIClient()
        client.force_authenticate(user=self.other)
        response = client.patch(f'/lessons/{self.lesson.id}/', {'title': 'Хак'})
        self.assertEqual(response.status_code, 404)

    def test_other_cannot_delete_lesson(self):
        client = APIClient()
        client.force_authenticate(user=self.other)
        response = client.delete(f'/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, 404)

    def test_anonymous_cannot_access(self):
        client = APIClient()
        self.assertIn(client.get('/courses/').status_code, (401, 403))
        self.assertIn(client.get('/lessons/').status_code, (401, 403))
