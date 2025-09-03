from django.core.management.base import BaseCommand

from lms.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    help = "Загрузка тестовых данных платежей"

    def handle(self, *args, **options):
        # Очищаем существующие платежи
        Payment.objects.all().delete()

        # Создаем тестовые платежи
        payments_data = [
            {
                "user": User.objects.get(username="admin"),
                "paid_course": Course.objects.get(name="Python-разработчик"),
                "paid_lesson": None,
                "amount": 150000.00,
                "payment_method": "transfer",
            },
            {
                "user": User.objects.get(username="admin"),
                "paid_course": Course.objects.get(name="Java-разработчик"),  # ← исправил название
                "paid_lesson": None,
                "amount": 180000.00,
                "payment_method": "transfer",
            },
            {
                "user": User.objects.get(username="admin"),
                "paid_course": None,
                "paid_lesson": Lesson.objects.get(name="Библиотеки для Python разработчика"),
                "amount": 2500.00,
                "payment_method": "transfer",
            },
        ]

        for payment_data in payments_data:
            Payment.objects.create(**payment_data)

        self.stdout.write(self.style.SUCCESS(f"Успешно создано {Payment.objects.count()} платежей"))
