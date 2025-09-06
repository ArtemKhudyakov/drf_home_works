from rest_framework import permissions


class CoursePermission(permissions.BasePermission):
    """
    Разрешение для курсов:
    - Модераторы: читать, редактировать
    - Владельцы: все действия
    - Остальные: только читать
    """

    def has_permission(self, request, view):
        is_moderator = request.user.groups.filter(name="Moderators").exists()

        if view.action in ["create"]:
            return not is_moderator  # Создавать могут все, кроме модераторов

        return True  # Для остальных действий проверяем на уровне объекта

    def has_object_permission(self, request, view, obj):
        is_moderator = request.user.groups.filter(name="Moderators").exists()
        is_owner = obj.owner == request.user

        if view.action in ["retrieve", "list"]:
            return True  # Читать могут все аутентифицированные

        elif view.action in ["update", "partial_update"]:
            return is_owner or is_moderator  # Редактировать могут владельцы и модераторы

        elif view.action == "destroy":
            return is_owner and not is_moderator  # Удалять могут только владельцы (не модераторы)

        return False


class LessonCreatePermission(permissions.BasePermission):
    """Разрешение для создания уроков"""

    def has_permission(self, request, view):
        is_moderator = request.user.groups.filter(name="Moderators").exists()
        return not is_moderator  # Создавать могут все, кроме модераторов


class LessonUpdatePermission(permissions.BasePermission):
    """Разрешение для редактирования уроков"""

    def has_object_permission(self, request, view, obj):
        is_moderator = request.user.groups.filter(name="Moderators").exists()
        is_owner = obj.owner == request.user
        return is_owner or is_moderator  # Владельцы и модераторы


class LessonDeletePermission(permissions.BasePermission):
    """Разрешение для удаления уроков"""

    def has_object_permission(self, request, view, obj):
        is_moderator = request.user.groups.filter(name="Moderators").exists()
        is_owner = obj.owner == request.user
        return is_owner and not is_moderator  # Только владельцы
