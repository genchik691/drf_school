# users/tests/test_tasks.py
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from users.models import User
from users.tasks import deactivate_inactive_users

class DeactivateInactiveUsersTest(TestCase):
    def test_deactivates_users_inactive_30_days(self):
        active = User.objects.create(email="active@test.com", is_active=True,
                                     last_login=timezone.now() - timedelta(days=5))
        inactive = User.objects.create(email="inactive@test.com", is_active=True,
                                       last_login=timezone.now() - timedelta(days=40))
        deactivate_inactive_users()
        active.refresh_from_db(); inactive.refresh_from_db()
        self.assertTrue(active.is_active)
        self.assertFalse(inactive.is_active)
        