from django.test import TestCase
from django.urls import reverse
from rest_framework import serializers, status
from rest_framework.test import APITestCase

from .models import Course, Lesson, Subscription
from .paginators import CoursePaginator, LessonPaginator
from .serializer import CourseSerializer, LessonSerializer
from .validators import YouTubeLinkValidator


class YouTubeValidatorTest(TestCase):

    def test_validator_valid_youtube_links(self):
        """Тест валидатора с разрешенными YouTube ссылками"""
        validator = YouTubeLinkValidator(fields=["video_link", "description"])

        valid_data = {
            "video_link": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "description": "Обучающее видео: https://youtu.be/test123",
        }

        # Не должно вызывать исключений
        try:
            validator(valid_data)
        except serializers.ValidationError:
            self.fail("Валидатор отверг валидные YouTube ссылки")

    def test_validator_invalid_links(self):
        """Тест валидатора с запрещенными ссылками"""
        validator = YouTubeLinkValidator(fields=["video_link", "description"])

        invalid_data = {
            "video_link": "https://vk.com/video123",
            "description": "Запрещенная ссылка: https://example.com/tutorial",
        }

        with self.assertRaises(serializers.ValidationError):
            validator(invalid_data)

    def test_validator_mixed_links(self):
        """Тест валидатора со смешанными ссылками"""
        validator = YouTubeLinkValidator(fields=["description"])

        mixed_data = {"description": "Хорошая ссылка: https://youtube.com/watch?v=test, плохая: https://vk.com/video"}

        with self.assertRaises(serializers.ValidationError):
            validator(mixed_data)

    def test_validator_empty_fields(self):
        """Тест валидатора с пустыми полями"""
        validator = YouTubeLinkValidator(fields=["video_link", "description"])

        empty_data = {"video_link": "", "description": None}

        # Не должно вызывать исключений
        try:
            validator(empty_data)
        except serializers.ValidationError:
            self.fail("Валидатор не должен падать на пустых полях")


class LessonSerializerTest(APITestCase):

    def setUp(self):
        """Создаем тестовый курс перед каждым тестом"""
        self.course = Course.objects.create(name="Test Course", description="Test course description")

    def test_lesson_serializer_valid_video_link(self):
        """Тест сериализатора урока с валидной YouTube ссылкой"""
        data = {
            "name": "Test Lesson",
            "description": "Lesson with YouTube video",
            "video_link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "course": self.course.id,  # Используем ID существующего курса
        }

        serializer = LessonSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_lesson_serializer_invalid_video_link(self):
        """Тест сериализатора урока с невалидной ссылкой"""
        data = {
            "name": "Test Lesson",
            "description": "Lesson with invalid video",
            "video_link": "https://vk.com/video123",
            "course": self.course.id,
        }

        serializer = LessonSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("video_link", serializer.errors)

    def test_lesson_serializer_invalid_description_links(self):
        """Тест сериализатора урока с запрещенными ссылками в описании"""
        data = {
            "name": "Test Lesson",
            "description": "Смотрите также: https://coursera.org/learn/python",
            "video_link": "https://youtube.com/watch?v=test",
            "course": self.course.id,
        }

        serializer = LessonSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("description", serializer.errors)

    def test_lesson_serializer_no_video_link(self):
        """Тест сериализатора урока без видео ссылки"""
        data = {
            "name": "Test Lesson",
            "description": "Lesson without video",
            "video_link": "",  # Пустая ссылка
            "course": self.course.id,
        }

        serializer = LessonSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class CourseSerializerTest(APITestCase):

    def test_course_serializer_valid_description(self):
        """Тест сериализатора курса с валидным описанием"""
        data = {"name": "Test Course", "description": "Курс с YouTube ссылками: https://youtu.be/test123"}

        serializer = CourseSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_course_serializer_invalid_description(self):
        """Тест сериализатора курса с запрещенными ссылками в описании"""
        data = {"name": "Test Course", "description": "Посетите наш сайт: https://example.com"}

        serializer = CourseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("description", serializer.errors)

    def test_course_serializer_no_links(self):
        """Тест сериализатора курса без ссылок"""
        data = {"name": "Test Course", "description": "Просто описание без ссылок"}

        serializer = CourseSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class SubscriptionAPITest(APITestCase):

    def setUp(self):
        # Создаем пользователя и курс
        from django.contrib.auth import get_user_model

        User = get_user_model()

        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        self.course = Course.objects.create(name="Test Course", description="Test course description")

        self.client.force_authenticate(user=self.user)
        self.subscription_url = reverse("lms:subscription")

    def test_add_subscription(self):
        """Тест добавления подписки"""
        data = {"course_id": self.course.id}
        response = self.client.post(self.subscription_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_remove_subscription(self):
        """Тест удаления подписки"""
        # Сначала добавляем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        data = {"course_id": self.course.id}
        response = self.client.post(self.subscription_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscription_without_course_id(self):
        """Тест без course_id"""
        response = self.client.post(self.subscription_url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_subscription_nonexistent_course(self):
        """Тест с несуществующим курсом"""
        data = {"course_id": 999}
        response = self.client.post(self.subscription_url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_is_subscribed_field_in_course(self):
        """Тест поля is_subscribed в сериализаторе курса"""
        # Запрос курса без подписки
        url = reverse("courses:course-detail", args=[self.course.id])  # ← Исправлено!
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_subscribed"])

        # Добавляем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        # Снова запрашиваем курс
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_subscribed"])


class PaginationTest(APITestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Создаем тестовые данные
        for i in range(15):
            Course.objects.create(name=f"Test Course {i}", description=f"Test course description {i}")

        course = Course.objects.first()
        for i in range(100):
            Lesson.objects.create(name=f"Test Lesson {i}", description=f"Test lesson description {i}", course=course)

        self.client.force_authenticate(user=self.user)

        # Используем реальные URL из дебага
        self.courses_url = "/courses/courses/"
        self.lessons_url = "/lessons/lessons_list/"

    def test_lesson_pagination_default(self):
        """Тест пагинации уроков по умолчанию"""
        response = self.client.get(self.lessons_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 5)  # page_size = 5
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

    def test_lesson_pagination_custom_size(self):
        """Тест пагинации уроков с кастомным размером"""
        response = self.client.get(f"{self.lessons_url}?page_size=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)

    def test_lesson_pagination_max_size(self):
        """Тест пагинации уроков с максимальным размером"""
        response = self.client.get(f"{self.lessons_url}?page_size=100")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ожидаем не более 50 элементов (max_page_size)
        expected_count = min(50, Lesson.objects.count())
        self.assertEqual(len(response.data["results"]), expected_count)

    def test_course_pagination_default(self):
        """Тест пагинации курсов по умолчанию"""
        response = self.client.get(self.courses_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)  # page_size = 5
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

    def test_course_pagination_custom_size(self):
        """Тест пагинации курсов с кастомным размером"""
        response = self.client.get(f"{self.courses_url}?page_size=3")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_course_pagination_max_size(self):
        """Тест пагинации курсов с максимальным размером"""
        response = self.client.get(f"{self.courses_url}?page_size=30")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ожидаем не более 20 элементов (max_page_size)
        expected_count = min(20, Course.objects.count())
        self.assertEqual(len(response.data["results"]), expected_count)

    # def test_course_pagination_default(self):
    #     """Тест пагинации курсов по умолчанию"""
    #     response = self.client.get('/courses/')
    #
    #     # Если 404, проверяем альтернативные URL
    #     if response.status_code == 404:
    #         response = self.client.get('/lms/courses/')  # Попробуем другой префикс
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('results', response.data)
    #     self.assertEqual(len(response.data['results']), 5)  # page_size = 5
    #     self.assertIn('count', response.data)
    #     self.assertIn('next', response.data)
    #     self.assertIn('previous', response.data)
    #
    # def test_course_pagination_custom_size(self):
    #     """Тест пагинации курсов с кастомным размером"""
    #     response = self.client.get('/courses/?page_size=3')
    #
    #     # Если 404, проверяем альтернативные URL
    #     if response.status_code == 404:
    #         response = self.client.get('/lms/courses/?page_size=3')
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data['results']), 3)
    #
    # def test_course_pagination_max_size(self):
    #     """Тест пагинации курсов с максимальным размером"""
    #     response = self.client.get('/courses/?page_size=30')
    #
    #     # Если 404, проверяем альтернативные URL
    #     if response.status_code == 404:
    #         response = self.client.get('/lms/courses/?page_size=30')
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # Ожидаем не более 20 элементов (max_page_size), но не более общего количества
    #     expected_count = min(20, Course.objects.count())
    #     self.assertEqual(len(response.data['results']), expected_count)


# class URLDebugTest(APITestCase):
#
#     def setUp(self):
#         from django.contrib.auth import get_user_model
#         User = get_user_model()
#         self.user = User.objects.create_user(username='test', password='test')
#         self.client.force_authenticate(user=self.user)
#
#     def test_debug_all_urls(self):
#         """Тест для отладки всех доступных URL"""
#         print("\n=== ДОСТУПНЫЕ URL ===")
#
#         # Проверяем возможные URL для курсов
#         test_urls = [
#             '/courses/',
#             '/lms/courses/',
#             '/courses/courses/',
#             '/lessons/courses/',
#             '/api/courses/',
#         ]
#
#         for url in test_urls:
#             response = self.client.get(url)
#             print(f"{url} -> {response.status_code}")
#             if response.status_code == 200:
#                 print(
#                     f"  Данные: {list(response.data.keys()) if hasattr(response.data, 'keys') else response.data}")
#
#         # Проверяем URL для уроков
#         print("\n=== URL УРОКОВ ===")
#         lesson_urls = [
#             '/lessons/lessons_list/',
#             '/lms/lessons/',
#             '/courses/lessons/',
#             '/api/lessons/',
#         ]
#
#         for url in lesson_urls:
#             response = self.client.get(url)
#             print(f"{url} -> {response.status_code}")
