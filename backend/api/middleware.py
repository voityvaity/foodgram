from django.utils.deprecation import MiddlewareMixin


class DisableCSRFForAPI(MiddlewareMixin):
    """Отключает CSRF проверку для API эндпоинтов."""

    def _should_disable_csrf(self, request):
        """Проверяет, нужно ли отключить CSRF для запроса."""
        api_paths = ['/api/', '/api/auth/']
        return any(request.path.startswith(path) for path in api_paths)

    def process_request(self, request):
        """Отключает CSRF для API эндпоинтов."""
        if self._should_disable_csrf(request):
            setattr(request, '_dont_enforce_csrf_checks', True)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Дополнительная проверка для view функций."""
        if self._should_disable_csrf(request):
            setattr(request, '_dont_enforce_csrf_checks', True)
