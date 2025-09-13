from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Course, Subscription, Lesson
from datetime import datetime, timedelta
from django.utils import timezone


@shared_task
def send_course_update_notification(course_id):
    """Отправка уведомления об обновлении курса с проверкой времени"""
    print(f"ЗАДАЧА ЗАПУЩЕНА для курса {course_id}")
    try:
        course = Course.objects.get(id=course_id)

        # Проверяем, когда курс последний раз обновлялся
        time_since_update = timezone.now() - course.updated_at

        # Если курс обновлялся менее 4 часов назад - не отправляем уведомление
        if time_since_update < timedelta(hours=4):
            return f"Курс обновлялся недавно ({time_since_update}), уведомление не отправлено"

        subscribers = Subscription.objects.filter(course=course)
        print(f"Найдено подписчиков: {subscribers.count()}")

        if subscribers.count() == 0:
            print("Нет подписчиков для уведомления")
            return "Нет подписчиков"

        for subscription in subscribers:
            print(f"ОТПРАВКА: {subscription.user.email}")

            # Отправка письма
            send_mail(
                subject=f'Обновление курса: {course.name}',
                message=f'Курс "{course.name}" был обновлен. Проверьте новые материалы!\n\n'
                        f'Перейти к курсу: http://127.0.0.1:8000/courses/courses/{course.id}/',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[subscription.user.email],
                fail_silently=False,
            )

            print(f"Письмо отправлено на: {subscription.user.email}")

        print(f"Уведомления отправлены для {subscribers.count()} подписчиков")
        return f"Уведомления отправлены для {subscribers.count()} подписчиков"

    except Exception as e:
        print(f"ОШИБКА: {e}")
        return f"Ошибка: {e}"


@shared_task
def check_inactive_users():
    """Проверка неактивных пользователей"""
    from users.models import User
    month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=month_ago, is_active=True)

    for user in inactive_users:
        send_mail(
            subject='Мы скучаем по вам!',
            message='Вы давно не заходили на нашу платформу. У нас есть новые интересные курсы!',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

    return f"Проверено {inactive_users.count()} неактивных пользователей"


@shared_task
def update_course_statistics():
    """Обновление статистики курсов"""
    courses = Course.objects.all()
    for course in courses:
        course.lessons_count = course.lesson_set.count()
        course.subscribers_count = course.subscriptions.count()
        course.save()

    return "Статистика курсов обновлена"


@shared_task
def check_lesson_updates():
    """Проверяет обновления уроков и отправляет уведомления по курсам"""
    four_hours_ago = timezone.now() - timedelta(hours=4)

    # Находим уроки, обновленные более 4 часов назад
    recent_lessons = Lesson.objects.filter(updated_at__gte=four_hours_ago)

    courses_to_notify = set()

    for lesson in recent_lessons:
        courses_to_notify.add(lesson.course.id)

    # Отправляем уведомления для каждого курса
    for course_id in courses_to_notify:
        send_course_update_notification.delay(course_id)

    return f"Проверено обновлений для {len(courses_to_notify)} курсов"