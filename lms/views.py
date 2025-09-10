from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.viewsets import ModelViewSet

from .models import Course, Lesson, Subscription
from .permissions import CoursePermission, LessonCreatePermission, LessonDeletePermission, LessonUpdatePermission
from .serializer import CourseSerializer, LessonSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .paginators import LessonPaginator, CoursePaginator

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="description from swagger_auto_schema via method_decorator"
))
class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all().order_by('id')
    serializer_class = CourseSerializer

    permission_classes = [permissions.IsAuthenticated, CoursePermission]
    pagination_class = CoursePaginator

    def get_serializer_context(self):
        """Передаем request в сериализатор для проверки подписки"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        """Все аутентифицированные пользователи видят все курсы"""
        return Course.objects.all().order_by('id')

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
    queryset = Lesson.objects.all().order_by('id')
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LessonPaginator

    def get_queryset(self):
        return Lesson.objects.all().order_by('id')


class SubscriptionAPIView(APIView):
    """API для управления подписками на курсы"""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {"error": "course_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            # Удаляем подписку
            subscription.delete()
            message = 'Подписка удалена'
        else:
            # Создаем подписку
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'

        return Response({"message": message}, status=status.HTTP_200_OK)