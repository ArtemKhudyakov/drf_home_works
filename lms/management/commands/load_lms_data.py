from django.core.management.base import BaseCommand
from django.core.management import call_command
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Полная перезагрузка данных LMS (очистка + загрузка фикстур)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Пропустить подтверждение'
        )

    def handle(self, *args, **options):
        if not options['noinput']:
            confirm = input(
                '⚠️  Вы уверены? Это удалит все существующие курсы и уроки. (y/N): '
            )
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Отменено.'))
                return

        self.stdout.write(self.style.WARNING('Очистка данных LMS...'))

        # Очищаем данные в правильном порядке (сначала уроки, потом курсы)
        Lesson.objects.all().delete()
        Course.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Данные очищены.'))
        self.stdout.write(self.style.SUCCESS('Загрузка фикстур...'))

        # Загружаем фикстуры
        try:
            call_command('loaddata', 'lms_data.json')
            self.stdout.write(
                self.style.SUCCESS('✅ Фикстуры успешно загружены!')
            )

            # Показываем статистику
            course_count = Course.objects.count()
            lesson_count = Lesson.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'📊 Загружено: {course_count} курсов, {lesson_count} уроков'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка загрузки фикстур: {e}')
            )
            # Если файл не найден, предлагаем создать его
            if "No such file or directory" in str(e):
                self.stdout.write(
                    self.style.NOTICE('💡 Создайте фикстуру командой:')
                )
                self.stdout.write(
                    self.style.NOTICE('python manage.py dumpdata lms --indent 2 --output lms/fixtures/lms_data.json')
                )