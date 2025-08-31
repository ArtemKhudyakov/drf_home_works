from rest_framework import permissions


class IsOwnerOrManager(permissions.BasePermission):
    """
    Разрешение: только владелец или менеджер могут редактировать профиль
    """

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено всем аутентифицированным
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Запись разрешена только владельцу или менеджеру
        return obj == request.user or request.user.role == "manager"
