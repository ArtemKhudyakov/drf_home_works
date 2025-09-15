from django.core.validators import FileExtensionValidator
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание курса")
    preview = models.ImageField(
        upload_to="courses/previews",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["jfif", "jpg", "jpeg", "png"])],
        verbose_name="Превьюшка курса",
        help_text="Загрузите изображение превьюшки курса",
    )
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
        help_text="Укажите владельца курса",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата последнего обновления",
        help_text="Автоматически обновляется при изменении курса"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        db_table = "Courses"


class Lesson(models.Model):
    name = models.CharField(max_length=300, verbose_name="Название урока")
    description = models.TextField(verbose_name="Описание урока")
    preview = models.ImageField(
        upload_to="lessons/previews",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["jfif", "jpg", "jpeg", "png"])],
        verbose_name="Превьюшка урока",
        help_text="Загрузите изображение превьюшки урока",
    )
    video_link = models.URLField(max_length=500, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Курс")
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
        help_text="Укажите владельца урока",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата последнего обновления"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        db_table = "lessons"


class Subscription(models.Model):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, verbose_name="Пользователь", related_name="subscriptions"
    )
    course = models.ForeignKey("Course", on_delete=models.CASCADE, verbose_name="Курс", related_name="subscriptions")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ["user", "course"]  # Одна подписка на пользователя и курс
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.course.name}"
