from rest_framework import serializers
from .models import Course, Lesson
from .validators import YouTubeLinkValidator

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [
            YouTubeLinkValidator(fields=['video_link', 'description'])
        ]

class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.IntegerField(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True, source="lesson_set")

    class Meta:
        model = Course
        fields = ["id", "name", "description", "preview", "lessons_count", "lessons", "owner"]
        validators = [
            YouTubeLinkValidator(fields=['description'])
        ]