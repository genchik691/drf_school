# lms/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from lms.models import Course, Lesson


class CourseSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.ru', password='test12345'
        )
        self.course = Course.objects.create(title='Django')
        Lesson.objects.create(title='Урок 1', course=self.course)
        Lesson.objects.create(title='Урок 2', course=self.course)

    def test_lessons_count(self):
        """lessons_count возвращает правильное количество."""
        client = APIClient()
        response = client.get(f'/courses/{self.course.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['lessons_count'], 2)

    def test_lessons_nested(self):
        """Вложенные уроки выводятся."""
        client = APIClient()
        response = client.get(f'/courses/{self.course.id}/')
        self.assertEqual(len(response.data['lessons']), 2)
