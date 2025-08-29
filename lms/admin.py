from django.contrib import admin
from .models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "preview")
    search_fields = ("name", "description")
    # list_filter = ("")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "preview", 'course', 'video_link')
    search_fields = ("name", "description")
    list_filter = ("course",)

