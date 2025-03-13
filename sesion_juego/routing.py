# sesion_juego/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/sesiones/(?P<codigo>\w+)/$', consumers.JuegoConsumer.as_asgi()),
]
