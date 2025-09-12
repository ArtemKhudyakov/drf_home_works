from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Course, Subscription
from datetime import datetime, timedelta
from django.utils import timezone


@shared_task
def send_course_update_notification(course_id):
    """Отправка уведомления об обновлении курса"""
    try:
        course = Course.objects.get(id=course_id)
        subscribers = Subscription.objects.filter(course=course)

        for subscription in subscribers:
            send_mail(
                subject=f'Обновление курса: {course.name}',
                message=f'Курс "{course.name}" был обновлен. Проверьте новые материалы!',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[subscription.user.email],
                fail_silently=False,
            )

        return f"Уведомления отправлены для {subscribers.count()} подписчиков"
    except Course.DoesNotExist:
        return "Курс не найден"


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