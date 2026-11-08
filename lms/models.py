# lms/models.py
from django.db import models
from django.conf import settings


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    preview = models.ImageField(upload_to='courses/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(  # ✅
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Владелец',
        null=True, blank=True,
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, null=True)
    preview = models.ImageField(upload_to='lessons/', blank=True, null=True)
    video_link = models.URLField(blank=True, null=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE,
        related_name='lessons', verbose_name='Курс'
    )
    owner = models.ForeignKey(  # ✅
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Владелец',
        null=True, blank=True,
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

    def __str__(self):
        return self.title
