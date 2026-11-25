# lms/tests/test_views.py
from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone
from rest_framework.test import APITestCase

from lms.models import Course, Subscription
from users.models import User


class CourseUpdateNotificationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(self.user)

    @patch("lms.views.send_course_update_email.delay")
    def test_no_email_if_updated_recently(self, mock_delay):
        course = Course.objects.create(
            owner=self.user,
            title="Test",
            updated_at=timezone.now() - timedelta(hours=1),
        )
        Subscription.objects.create(user=self.user, course=course)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(
                f"/courses/{course.pk}/", {"title": "Updated"}
            )

        self.assertEqual(response.status_code, 200)
        mock_delay.assert_not_called()

    @patch("lms.views.send_course_update_email.delay")
    def test_email_sent_if_updated_long_ago(self, mock_delay):
        course = Course.objects.create(owner=self.user, title="Test")
        Subscription.objects.create(user=self.user, course=course)

        # «Состариваем» курс в обход auto_now=True
        Course.objects.filter(pk=course.pk).update(
            updated_at=timezone.now() - timedelta(hours=5)
        )
        course.refresh_from_db()

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(
                f"/courses/{course.pk}/", {"title": "Updated"}
            )

        self.assertEqual(response.status_code, 200)
        mock_delay.assert_called_once_with("owner@example.com", "Updated")

