from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    CourseViewSet,
    LessonCreateAPIView,
    LessonDestroyAPIView,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView
)

app_name = "lms"

router = SimpleRouter()
router.register(r"courses", CourseViewSet)

urlpatterns = [
    path("lessons_list/", LessonListAPIView.as_view(), name="lessons_list"),
    path("lesson/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson"),
    path("lesson/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path("lesson/<int:pk>/delete/", LessonDestroyAPIView.as_view(), name="lesson-delete"),
    path("lesson/update/<int:pk>/update/", LessonUpdateAPIView.as_view(), name="lesson-update"),
] + router.urls
