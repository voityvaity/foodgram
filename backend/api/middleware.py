from django.utils.deprecation import MiddlewareMixin


class DisableCSRFForAPI(MiddlewareMixin):
    """Отключает CSRF для API запросов."""
    
    def process_request(self, request):
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)


class NoCacheMiddleware(MiddlewareMixin):
    """Отключает кэширование для медиафайлов и API."""
    
    def process_response(self, request, response):
        # Отключаем кэширование для медиафайлов и API
        if (request.path.startswith('/media/') or 
            request.path.startswith('/api/')):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['Last-Modified'] = response.get('Last-Modified', '')
            response['ETag'] = ''
        return response