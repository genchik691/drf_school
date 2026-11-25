# drf_school/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drf_school.settings")

app = Celery("drf_school")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Расписание (для Задания 3)
app.conf.beat_schedule = {
    "deactivate-inactive-users": {
        "task": "users.tasks.deactivate_inactive_users",
        "schedule": crontab(hour=3, minute=0),  # каждый день в 03:00
    },
}