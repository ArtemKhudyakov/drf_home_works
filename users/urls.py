from django.contrib.auth.views import LoginView
from django.urls import path, reverse_lazy
from .views import (
    CustomLogoutView,
    UserRegisterView,
    UserProfileUpdateView,
    email_verification,
)
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm

from .views import UserListView, toggle_user_block

app_name = 'users'

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/", UserRegisterView.as_view(template_name="users/registration.html"), name="register"),
    path("profile/edit/", UserProfileUpdateView.as_view(), name="profile_edit"),
    path("email-confirm/<str:token>/", email_verification, name="email_verification"),

    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             form_class=CustomPasswordResetForm,
             template_name='users/password_reset.html',
             email_template_name='users/password_reset_email.html',
             subject_template_name='users/password_reset_subject.txt',
             success_url=reverse_lazy('users:password_reset_done')
         ), name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html',
         ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete'),
         ), name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html',
         ), name='password_reset_complete'),
    path('manager/users/', UserListView.as_view(), name='user_list'),
    path('manager/users/toggle_block/<int:user_id>/', toggle_user_block, name='toggle_user_block'),
]
