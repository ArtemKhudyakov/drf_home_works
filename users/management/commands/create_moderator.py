from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Create a moderator user'

    def handle(self, *args, **options):
        User = get_user_model()

        moderators_group, created = Group.objects.get_or_create(name='Moderators')

        if created:
            course_content_type = ContentType.objects.get_for_model(Course)
            lesson_content_type = ContentType.objects.get_for_model(Lesson)

            content_permissions = Permission.objects.filter(
                content_type__in=[course_content_type, lesson_content_type],
                codename__in=['view_course', 'change_course', 'view_lesson', 'change_lesson']
            )
            moderators_group.permissions.set(content_permissions)

            self.stdout.write(
                self.style.SUCCESS('Группа Moderators создана с ограниченными правами')
            )

        # Создаем модератора
        moderator = User.objects.create(
            email='temp@mail.ru',
        )

        id = moderator.id
        moderator.username = f'moderator_{id}'
        moderator.email = f'{moderator.username}@mail.ru'
        moderator.role = "moderator"
        moderator.is_staff = True
        moderator.is_active = True
        moderator.set_password(f'{moderator.username}')
        moderator.is_verified = True
        moderator.save()

        moderator.groups.add(moderators_group)

        moderator.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Модератор создан:\n'
                f'Email: {moderator.email}\n'
                f'Username: {moderator.username}\n'
                f'Password: {moderator.username}\n'
                f'Role: {moderator.role}'
            )
        )