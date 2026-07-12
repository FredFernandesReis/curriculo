"""Middleware para facilitar testes com ngrok em desenvolvimento."""
from django.conf import settings


class NgrokCsrfMiddleware:
    """Confia automaticamente em origens ngrok durante o desenvolvimento."""

    NGROK_SUFFIXES = ('.ngrok-free.app', '.ngrok.io', '.ngrok.app')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            host = request.get_host().split(':')[0]
            if host.endswith(self.NGROK_SUFFIXES):
                origin = f'https://{request.get_host()}'
                if origin not in settings.CSRF_TRUSTED_ORIGINS:
                    settings.CSRF_TRUSTED_ORIGINS.append(origin)
        return self.get_response(request)
