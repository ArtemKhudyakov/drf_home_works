from django.core.management import BaseCommand

from django.contrib.auth import get_user_model

from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Create a moderator user'

    def handle(self, *args, **options):
        User = get_user_model()
        num_of_users = User.objects.count()

        moderators_group, created = Group.objects.get_or_create(name='Moderators')

        if created:

            content_permissions = Permission.objects.filter(
                codename__in=['change_course', 'view_course', 'change_lesson', 'view_lesson']
            )
            moderators_group.permissions.set(content_permissions)
            self.stdout.write(
                self.style.SUCCESS('Группа Moderators создана с необходимыми разрешениями')
            )

        moderator = User.objects.create(
            email='empty@mail.ru',
        )

        id = moderator.id

        moderator.username = f'Moderator_{id}'
        moderator.email = f'{moderator.username}@mail.ru'

        self.stdout.write(
            self.style.SUCCESS(f'Модератор успешно создан: {moderator.username}')
        )
        moderator.is_staff = True
        moderator.is_active = True
        moderator.set_password(raw_password=f'moderator{moderator.username}')

        moderator.save()