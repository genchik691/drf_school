# lms/views.py
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsModerator, IsOwnerOrModerator
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        # ✅ создание и удаление — только не модераторы
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), ~IsModerator()]
        # ✅ редактирование — владелец или модератор
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsOwnerOrModerator()]
        # ✅ просмотр — авторизованные
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), ~IsModerator()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), ~IsModerator()]
        return [IsAuthenticated(), IsOwnerOrModerator()]
    