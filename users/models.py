from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import FileExtensionValidator


class User(AbstractUser):
    username = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Имя пользователя",
        help_text="Введите имя пользователя",
    )
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        verbose_name="email",
        help_text="Введите адрес электронной почты",
    )
    country = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Страна",
        help_text="Введите страну",
    )
    phone = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Введите номер телефона",
    )
    avatar = models.ImageField(
        upload_to="users/avatars",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["jfif", "jpg", "jpeg", "png"])],
        verbose_name="Аватар",
        help_text="Загрузите изображение аватара",
    )
    token = models.CharField(max_length=100, verbose_name="Токен", blank=True, null=True)
    is_verified = models.BooleanField(default=False, verbose_name="Подтвержден")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    ROLES = (
        ('user', 'Пользователь'),
        ('manager', 'Менеджер'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLES,
        default='user',
        verbose_name="Роль"
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name="Заблокирован"
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        db_table = "users"
        permissions = [
            ("block_user", "Может блокировать пользователей"),
            ("disable_mailing", "Может отключать рассылки"),
        ]
