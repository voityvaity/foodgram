from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее только владельцу объекта редактировать его.
    Универсально работает для obj.author и obj.user.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение любому
        if request.method in permissions.SAFE_METHODS:
            return True

        # Проверяем аутентификацию
        if not request.user or not request.user.is_authenticated:
            return False

        # Проверяем возможные поля владельца
        owner = getattr(obj, 'author', None) or getattr(obj, 'user', None)

        # Если поле владельца есть, сравниваем с request.user
        if owner:
            return owner == request.user

        # Если поля нет, запрещаем запись
        return False


class IsAuthenticatedOrCreateOnly(permissions.BasePermission):
    """
    Разрешение, позволяет неаутентифицированным пользователям
    только создавать пользователей.
    """

    def has_permission(self, request, view):
        if view.action == 'create':
            return True
        return request.user and request.user.is_authenticated


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее только автору рецепта редактировать и удалять его.
    """

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено для любого запроса
        if request.method in permissions.SAFE_METHODS:
            return True

        # Проверяем аутентификацию
        if not request.user or not request.user.is_authenticated:
            return False

        # Запись разрешена только автору
        return obj.author == request.user
