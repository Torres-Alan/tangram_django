"""
ASGI config for tangram_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# tangram_project/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from sesion_juego.routing import websocket_urlpatterns  # Esta es la ruta para el WebSocket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tangram_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)  # Este es el router para WebSocket
    ),
})
