import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, ListView, TemplateView, UpdateView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from .filters import PaymentFilter
from .forms import UserProfileForm, UserRegistrationForm
from .mixins import ManagerRequiredMixin
from .models import Payment, User
from .permissions import CanEditUserProfile, CanViewUserList
from .serializers import (
    PaymentSerializer,
    UserApiRegistrationSerializer,
    UserPrivateProfileSerializer,
    UserPublicProfileSerializer
)
from .services import convert_rub_into_usd, create_stripe_session, create_stripe_price


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("home")


class UserRegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("home")

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
@method_decorator(cache_page(60 * 10), name="dispatch")
class UserListView(ManagerRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"


# Блокировка/разблокировка пользователей
def toggle_user_block(request, user_id):
    if request.user.role != "manager":
        raise PermissionDenied

    user = get_object_or_404(User, id=user_id)
    user.is_blocked = not user.is_blocked
    user.save()
    messages.success(request, f"Пользователь {user.email} {'заблокирован' if user.is_blocked else 'разблокирован'}")
    return redirect("users:user_list")


class UserProfileUpdateAPIView(generics.UpdateAPIView):
    """
    Эндпоинт для редактирования профиля пользователя
    Доступ: владелец, менеджер или админ
    """

    serializer_class = UserPrivateProfileSerializer
    permission_classes = [permissions.IsAuthenticated, CanEditUserProfile]

    def get_object(self):
        """Вызываем проверку прав для объекта"""
        user_id = self.kwargs.get("pk")
        if user_id:
            user = generics.get_object_or_404(User, pk=user_id)

            # Явно вызываем проверку прав для объекта
            self.check_object_permissions(self.request, user)
            return user
        return self.request.user

    # class UserProfileUpdateAPIView(generics.UpdateAPIView):
    #     serializer_class = UserPrivateProfileSerializer
    #     permission_classes = [permissions.IsAuthenticated, CanEditUserProfile]
    #
    #     def get_object(self):
    #         user_id = self.kwargs.get("pk")
    #         if user_id:
    #             user = generics.get_object_or_404(User, pk=user_id)
    #
    #             # Дополнительная debug проверка для админа
    #             current_user = self.request.user
    #             if user != current_user and (current_user.is_staff or current_user.is_superuser):
    #                 print(f"🛠️ Admin override: {current_user} editing {user}")
    #
    #             self.check_object_permissions(self.request, user)
    #             return user
    #         return self.request.user

    def check_object_permissions(self, request, obj):
        """Вызываем проверку всех permission классов для объекта"""

        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied("Недостаточно прав для редактирования этого профиля")


class UserProfileRetrieveAPIView(generics.RetrieveAPIView):
    """
    Эндпоинт для просмотра профиля пользователя
    - Владелец: все данные
    - Менеджер/Админ: все данные любого профиля
    - Обычный пользователь: только публичные данные чужого профиля
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        target_user = self.get_object()
        current_user = self.request.user

        # Владелец видит все свои данные
        if target_user == current_user:
            return UserPrivateProfileSerializer

        # Менеджер/Админ видит все данные любого пользователя
        is_manager = getattr(current_user, "role", None) == "manager"
        is_admin = current_user.is_staff
        if is_manager or is_admin:
            return UserPrivateProfileSerializer

        # Обычный пользователь видит только публичные данные чужого профиля
        return UserPublicProfileSerializer

    def get_object(self):
        user_id = self.kwargs.get("pk")
        if user_id:
            return generics.get_object_or_404(User, pk=user_id)
        return self.request.user


User = get_user_model()


class UserListAPIView(generics.ListAPIView):
    """
    Эндпоинт для просмотра списка пользователей
    Только для менеджеров и админов
    """

    serializer_class = UserPrivateProfileSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewUserList]

    def get_queryset(self):
        # Проверяем права
        if not (self.request.user.role == "manager" or self.request.user.is_staff):
            raise DRFPermissionDenied("Только менеджеры и администраторы могут просматривать список пользователей")

        return User.objects.all().order_by("-date_joined")


class UserListHTMLView(ManagerRequiredMixin, TemplateView):
    """HTML страница списка пользователей"""

    template_name = "users/user_list_api.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all().order_by("-date_joined")
        return context


class PaymentListAPIView(generics.ListAPIView):
    """Эндпоинт для получения списка платежей с фильтрацией"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]  # сортировка по умолчанию


class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    """Эндпоинт для получения детальной информации о платеже"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentCreateAPIView(generics.CreateAPIView):
    """Эндпоинт для создания нового платежа"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        user = self.request.user
        amount_in_usd = convert_rub_into_usd(payment.amount)
        price = create_stripe_price(amount_in_usd)
        session_id, payment_link = create_stripe_session(price)
        payment.session_id = session_id
        payment.payment_link = payment_link
        payment.save()


class PaymentUpdateAPIView(generics.UpdateAPIView):
    """Эндпоинт для обновления платежа"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentDestroyAPIView(generics.DestroyAPIView):
    """Эндпоинт для удаления платежа"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class UserCreateApiView(generics.CreateAPIView):
    serializer_class = UserApiRegistrationSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()
