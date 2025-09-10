from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from lms.models import Course, Lesson


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

    city = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Введите город",
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

    ROLES = (("user", "Пользователь"), ("manager", "Менеджер"), ("moderator", "Модератор"))
    role = models.CharField(max_length=10, choices=ROLES, default="user", verbose_name="Роль")
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокирован")

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


class Payment(models.Model):
    PAYMENT_METHODS = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счет"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="payments")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Оплаченный курс",
        null=True,
        blank=True,
        related_name="payments",
    )
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        verbose_name="Оплаченный урок",
        null=True,
        blank=True,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, verbose_name="Способ оплаты")
    session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="id сессии",
        help_text="введите id сессии"
    )
    link_for_pay = models.URLField(
        max_length=400,
        blank=True,
        null=True,
        verbose_name="Ссыллка на оплату",
        help_text="введите ссылку на оплату"
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Платеж {self.user.username} - {self.amount} руб. ({self.get_payment_method_display()})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.paid_course and self.paid_lesson:
            raise ValidationError("Можно оплатить либо курс, либо урок, но не оба одновременно.")
        if not self.paid_course and not self.paid_lesson:
            raise ValidationError("Должен быть указан либо курс, либо урок.")
