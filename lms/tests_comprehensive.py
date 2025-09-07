from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from lms.models import Course, Lesson, Subscription
from users.models import User


class LessonCRUDTest(APITestCase):
    """
    Тесты CRUD операций для уроков с разными правами доступа
    """

    def setUp(self):
        # Создаем пользователей с разными ролями
        self.user = User.objects.create_user(
            username='test_user',
            email='user@example.com',
            password='testpass123',
            role='user'
        )

        self.moderator = User.objects.create_user(
            username='test_moderator',
            email='moderator@example.com',
            password='testpass123',
            role='moderator'
        )

        self.manager = User.objects.create_user(
            username='test_manager',
            email='manager@example.com',
            password='testpass123',
            role='manager'
        )

        # Создаем курс
        self.course = Course.objects.create(
            name='Test Course',
            description='Test Course Description',
            owner=self.user  # Владелец - обычный пользователь
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Lesson Description',
            course=self.course,
            owner=self.user  # Владелец - обычный пользователь
        )

        # URL для уроков
        self.lesson_list_url = reverse('lessons:lessons_list')
        self.lesson_detail_url = reverse('lessons:lesson', args=[self.lesson.id])
        self.lesson_create_url = reverse('lessons:lesson-create')
        self.lesson_update_url = reverse('lessons:lesson-update', args=[self.lesson.id])
        self.lesson_delete_url = reverse('lessons:lesson-delete', args=[self.lesson.id])

    def test_lesson_list_authenticated(self):
        """Тест получения списка уроков аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.lesson_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_lesson_list_unauthenticated(self):
        """Тест получения списка уроков неаутентифицированным пользователем"""
        response = self.client.get(self.lesson_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_detail_authenticated(self):
        """Тест получения деталей урока аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Lesson')

    def test_lesson_create_by_user(self):
        """Тест создания урока обычным пользователем"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'New Lesson',
            'description': 'New Lesson Description',
            'course': self.course.id,
            'video_link': 'https://youtube.com/watch?v=test'
        }
        response = self.client.post(self.lesson_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_update_by_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Updated Lesson Name'}
        response = self.client.patch(self.lesson_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, 'Updated Lesson Name')

    def test_lesson_update_by_other_user(self):
        """Тест обновления урока другим пользователем (должно быть запрещено)"""
        other_user = User.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=other_user)
        data = {'name': 'Updated by Other User'}
        response = self.client.patch(self.lesson_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_delete_by_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.lesson_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_delete_by_moderator(self):
        """Тест удаления урока модератором (должно быть запрещено)"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(self.lesson_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_lesson_with_invalid_video_link(self):
        """Тест создания урока с невалидной видео ссылкой"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Invalid Link Lesson',
            'description': 'Lesson with invalid video link',
            'course': self.course.id,
            'video_link': 'https://vk.com/video123'  # Не YouTube!
        }
        response = self.client.post(self.lesson_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.data)


class SubscriptionTest(APITestCase):
    """
    Тесты функционала подписок на курсы
    """

    def setUp(self):
        # Создаем пользователей
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )

        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )

        # Создаем курс
        self.course = Course.objects.create(
            name='Test Course for Subscription',
            description='Test Course Description'
        )

        # URL для подписок
        self.subscription_url = reverse('lessons:subscription')

    def test_add_subscription(self):
        """Тест добавления подписки"""
        self.client.force_authenticate(user=self.user1)
        data = {'course_id': self.course.id}

        response = self.client.post(self.subscription_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.user1, course=self.course).exists())

    def test_remove_subscription(self):
        """Тест удаления подписки"""
        # Сначала добавляем подписку
        Subscription.objects.create(user=self.user1, course=self.course)

        self.client.force_authenticate(user=self.user1)
        data = {'course_id': self.course.id}

        response = self.client.post(self.subscription_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user1, course=self.course).exists())

    def test_subscription_different_users(self):
        """Тест что подписки разных пользователей не пересекаются"""
        # User1 подписывается
        self.client.force_authenticate(user=self.user1)
        data = {'course_id': self.course.id}
        response = self.client.post(self.subscription_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User2 проверяет что не подписан
        self.client.force_authenticate(user=self.user2)
        url = reverse('courses:course-detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_subscribed'])

    def test_subscription_without_course_id(self):
        """Тест подписки без course_id"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.subscription_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_subscription_nonexistent_course(self):
        """Тест подписки на несуществующий курс"""
        self.client.force_authenticate(user=self.user1)
        data = {'course_id': 9999}  # Несуществующий ID
        response = self.client.post(self.subscription_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_is_subscribed_field(self):
        """Тест поля is_subscribed в сериализаторе курса"""
        # User1 подписывается
        Subscription.objects.create(user=self.user1, course=self.course)

        self.client.force_authenticate(user=self.user1)
        url = reverse('courses:course-detail', args=[self.course.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

        # User2 не подписан
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_subscribed'])


class PermissionTest(APITestCase):
    """
    Тесты прав доступа для разных ролей пользователей
    """

    def setUp(self):
        # Создаем пользователей с разными ролями
        self.user = User.objects.create_user(
            username='regular_user',
            email='user@example.com',
            password='testpass123',
            role='user'
        )

        self.moderator = User.objects.create_user(
            username='moderator_user',
            email='moderator@example.com',
            password='testpass123',
            role='moderator'
        )

        self.manager = User.objects.create_user(
            username='manager_user',
            email='manager@example.com',
            password='testpass123',
            role='manager'
        )

        # Создаем курс от имени обычного пользователя
        self.course = Course.objects.create(
            name='Test Course',
            description='Test Course Description',
            owner=self.user
        )

        # Создаем урок от имени обычного пользователя
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Lesson Description',
            course=self.course,
            owner=self.user
        )

        # URL
        self.lesson_list_url = reverse('lessons:lessons_list')
        self.course_list_url = reverse('courses:course-list')

    def test_access_to_lessons_list(self):
        """Тест доступа к списку уроков для разных ролей"""
        # Все аутентифицированные пользователи должны иметь доступ
        for user in [self.user, self.moderator, self.manager]:
            self.client.force_authenticate(user=user)
            response = self.client.get(self.lesson_list_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_to_courses_list(self):
        """Тест доступа к списку курсов для разных ролей"""
        # Все аутентифицированные пользователи должны иметь доступ
        for user in [self.user, self.moderator, self.manager]:
            self.client.force_authenticate(user=user)
            response = self.client.get(self.course_list_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)