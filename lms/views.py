from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.viewsets import ModelViewSet

from rest_framework import permissions

from .models import Course, Lesson
from .serializer import CourseSerializer, LessonSerializer
from .permissions import CoursePermission, LessonCreatePermission, LessonUpdatePermission, LessonDeletePermission


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    permission_classes = [permissions.IsAuthenticated, CoursePermission]

    def get_queryset(self):
        """Все аутентифицированные пользователи видят все курсы"""
        return Course.objects.all()

    def perform_create(self, serializer):
        """При создании курса назначаем владельца"""
        course = serializer.save()
        course.owner = self.request.user
        course.save()


class LessonCreateAPIView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, LessonCreatePermission]

    def perform_create(self, serializer):
        lesson = serializer.save()
        lesson.owner = self.request.user
        lesson.save()


class LessonDestroyAPIView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, LessonDeletePermission]


class LessonUpdateAPIView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, LessonUpdatePermission]


class LessonRetrieveAPIView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]


class LessonListAPIView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.all()
