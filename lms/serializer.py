from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.IntegerField(read_only=True)  # ← serializers.IntegerField!
    lessons = LessonSerializer(many=True, read_only=True, source="lesson_set")

    class Meta:
        model = Course
        fields = ["id", "name", "description", "preview", "lessons_count", "lessons", "owner"]
