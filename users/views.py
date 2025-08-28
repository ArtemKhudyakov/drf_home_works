from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from django.views.generic import CreateView, UpdateView
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail

from .forms import UserRegistrationForm, UserProfileForm
from .models import User
from django.conf import settings

from django.views.generic import ListView
from .mixins import ManagerRequiredMixin

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

import secrets


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("greeting")


class UserRegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("users:profile_edit")

    def form_valid(self, form):

        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"""Здравствуйте {user.username}.
Пожалуйста, подтвердите Ваш адрес электронной почты для завершения регистрации.
для этого перейдите по ссылке {url}""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        response = super().form_valid(form)
        login(self.request, user)
        messages.success(self.request, "Регистрация прошла успешно!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме")
        return super().form_invalid(form)


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile_edit")

    def get_object(self, queryset=None):
        return self.request.user  # Редактируем текущего пользователя


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.is_verified = True
    user.token = None
    user.save()

    # Автоматически авторизуем пользователя
    login(request, user)

    # Добавляем сообщение об успехе
    messages.success(request, "Ваш email успешно подтвержден!")

    # Редирект на страницу профиля
    return redirect("users:profile_edit")


# Список всех пользователей (только для менеджеров)
@method_decorator(cache_page(60 * 10), name='dispatch')
class UserListView(ManagerRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'


# Блокировка/разблокировка пользователей
def toggle_user_block(request, user_id):
    if request.user.role != 'manager':
        raise PermissionDenied

    user = get_object_or_404(User, id=user_id)
    user.is_blocked = not user.is_blocked
    user.save()
    messages.success(request, f"Пользователь {user.email} {'заблокирован' if user.is_blocked else 'разблокирован'}")
    return redirect('users:user_list')
