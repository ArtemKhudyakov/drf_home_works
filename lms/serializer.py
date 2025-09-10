from rest_framework import serializers

from .models import Course, Lesson, Subscription
from .validators import YouTubeLinkValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [YouTubeLinkValidator(fields=["video_link", "description"])]


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.IntegerField(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True, source="lesson_set")
    is_subscribed = serializers.SerializerMethodField()  # Новое поле

    class Meta:
        model = Course
        fields = ["id", "name", "description", "preview", "lessons_count", "lessons", "owner", "is_subscribed"]
        validators = [YouTubeLinkValidator(fields=["description"])]

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False
