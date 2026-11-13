# lms/serializers.py
from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор урока с валидацией ссылки на YouTube."""
    video_link = serializers.URLField(
        validators=[validate_youtube_url],
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_link', 'course', 'owner']
        read_only_fields = ['owner']


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса с вложенными уроками и признаком подписки."""
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'preview', 'description',
            'lessons', 'lessons_count', 'is_subscribed', 'owner',
        ]
        read_only_fields = ['owner']

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscriptions.filter(user=request.user).exists()
        return False
