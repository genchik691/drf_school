from unittest.mock import patch

from django.test import TestCase

from lms.tasks import send_course_update_email


class SendCourseUpdateEmailTest(TestCase):
    @patch("lms.tasks.send_mail")
    def test_sends_email_to_subscriber(self, mock_send_mail):
        send_course_update_email.apply(args=("user@example.com", "Python Course"))

        mock_send_mail.assert_called_once()
        _, kwargs = mock_send_mail.call_args

        self.assertEqual(kwargs["subject"], "Обновление курса: Python Course")
        self.assertEqual(
            kwargs["message"],
            "Курс «Python Course» был обновлён. Проверьте новые материалы.",
        )
        self.assertEqual(kwargs["recipient_list"], ["user@example.com"])
        # Проверяем, что адрес отправителя взят из настроек
        from django.conf import settings
        self.assertEqual(kwargs["from_email"], settings.DEFAULT_FROM_EMAIL)

    @patch("lms.tasks.send_mail", side_effect=Exception("SMTP down"))
    def test_retries_on_failure(self, mock_send_mail):
        result = send_course_update_email.apply(args=("user@example.com", "Python Course"))
        self.assertTrue(result.failed())
        expected_calls = send_course_update_email.max_retries + 1
        self.assertEqual(mock_send_mail.call_count, expected_calls)
