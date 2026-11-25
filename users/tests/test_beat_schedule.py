# users/tests/test_beat_schedule.py
from django.test import TestCase
from drf_school.celery import app

class BeatScheduleTest(TestCase):
    def test_deactivate_task_in_schedule(self):
        self.assertIn("deactivate-inactive-users", app.conf.beat_schedule)
        self.assertEqual(
            app.conf.beat_schedule["deactivate-inactive-users"]["task"],
            "users.tasks.deactivate_inactive_users",
        )
