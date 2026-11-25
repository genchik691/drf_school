# lms/views.py
from datetime import timedelta

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsModerator, NotIsModerator, IsOwnerOrModerator

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from .tasks import send_course_update_email

# Порог: не отправлять уведомление, если курс обновлялся менее 4 часов назад
COURSE_UPDATE_COOLDOWN = timedelta(hours=4)


def notify_course_subscribers(course: Course, previous_updated_at) -> None:
    """
    Отправляет письма подписчикам курса, если с прошлого обновления
    прошло больше COURSE_UPDATE_COOLDOWN.

    previous_updated_at — значение course.updated_at ДО текущего save().

    Отправка оборачивается в transaction.on_commit: если транзакция
    откатится, письмо не уйдёт.
    """
    if previous_updated_at is not None:
        elapsed = timezone.now() - previous_updated_at
        if elapsed < COURSE_UPDATE_COOLDOWN:
            return  # уведомление не отправляем — курс обновлялся недавно

    subscribers = (
        Subscription.objects
        .filter(course=course)
        .select_related("user")
    )
    for sub in subscribers:
        if not sub.user.email:
            continue
        # Фиксируем значения в локальных переменных, чтобы избежать
        # late-binding в lambda (иначе все задачи получат данные
        # последнего подписчика).
        email = sub.user.email
        title = course.title
        transaction.on_commit(
            lambda email=email, title=title: (
                send_course_update_email.delay(email, title)
            )
        )


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Управление подпиской на курс",
        description="Создаёт подписку, если её нет. Удаляет, если есть.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "course_id": {"type": "integer", "description": "ID курса"}
                },
                "required": ["course_id"],
            }
        },
        responses={
            200: OpenApiResponse(description="Подписка удалена"),
            201: OpenApiResponse(description="Подписка добавлена"),
            400: OpenApiResponse(description="course_id не передан"),
            404: OpenApiResponse(description="Курс не найден"),
        },
    )
    def post(self, request, *args, **kwargs):
        course_id = request.data.get("course_id")
        if not course_id:
            return Response(
                {"error": "Поле course_id обязательно"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = get_object_or_404(Course, id=course_id)
        subscription = Subscription.objects.filter(
            user=request.user,
            course=course,
        ).first()

        if subscription:
            subscription.delete()
            return Response(
                {"message": "Подписка удалена"},
                status=status.HTTP_200_OK,
            )

        Subscription.objects.create(user=request.user, course=course)
        return Response(
            {"message": "Подписка добавлена"},
            status=status.HTTP_201_CREATED,
        )


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            return Course.objects.all().select_related("owner")
        return Course.objects.filter(owner=user).select_related("owner")

    def get_permissions(self):
        if self.action in ["create", "destroy"]:
            return [IsAuthenticated(), NotIsModerator()]
        if self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), IsOwnerOrModerator()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        # 1) Запоминаем updated_at ДО save(), пока он ещё старый
        previous_updated_at = serializer.instance.updated_at

        # 2) Успешное обновление
        course = serializer.save()

        # 3) Рассылка подписчикам (с проверкой 4-часового кулдауна)
        notify_course_subscribers(course, previous_updated_at)


class CourseUpdateAPIView(generics.UpdateAPIView):
    """
    Legacy-эндпоинт обновления курса.

    Оставлен для обратной совместимости API. Логика полностью
    делегируется notify_course_subscribers, чтобы поведение совпадало
    с CourseViewSet.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_update(self, serializer):
        previous_updated_at = serializer.instance.updated_at
        course = serializer.save()
        notify_course_subscribers(course, previous_updated_at)


class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all().select_related("owner", "course")
        return Lesson.objects.filter(owner=user).select_related("owner", "course")

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), NotIsModerator()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all().select_related("owner", "course")
        return Lesson.objects.filter(owner=user).select_related("owner", "course")

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), NotIsModerator()]
        return [IsAuthenticated(), IsOwnerOrModerator()]

    def perform_update(self, serializer):
        # Доп. задание: уведомление при обновлении урока.
        # previous_updated_at берём из course, к которому относится урок.
        lesson = serializer.instance
        course = lesson.course
        previous_course_updated_at = course.updated_at if course else None

        lesson = serializer.save()

        if course:
            # Обновляем updated_at курса через save(), а не .update(),
            # чтобы не обходить auto_now (если оно задано на поле)
            # и сохранить консистентность объекта в памяти.
            course.updated_at = timezone.now()
            course.save(update_fields=["updated_at"])
            course.refresh_from_db(fields=["updated_at"])

            notify_course_subscribers(course, previous_course_updated_at)
