# users/tasks.py
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@shared_task
def deactivate_inactive_users() -> int:
    """
    Блокирует пользователей, не заходивших более 30 дней.
    Батчевое обновление через QuerySet.update() — один SQL-запрос.
    """
    cutoff = timezone.now() - timedelta(days=30)

    # Батч: один UPDATE ... WHERE last_login < cutoff AND is_active = True
    updated_count = User.objects.filter(
        last_login__lt=cutoff,
        is_active=True,
    ).update(is_active=False)

    return updated_count
