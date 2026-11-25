# lms/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_course_update_email(self, email: str, course_title: str) -> str:
    """Отправка письма подписчику об обновлении курса."""
    try:
        send_mail(
            subject=f"Обновление курса: {course_title}",
            message=f"Курс «{course_title}» был обновлён. Проверьте новые материалы.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return f"Email sent to {email}"
    except Exception as exc:
        raise self.retry(exc=exc)
