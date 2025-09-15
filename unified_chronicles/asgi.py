"""
ASGI config for unified_chronicles project.
Supports both HTTP and WebSocket connections for real-time chat.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unified_chronicles.settings')

django_asgi_app = get_asgi_application()

# Import after Django setup
try:
    from mensagens.routing import websocket_urlpatterns
except ImportError:
    websocket_urlpatterns = []

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
