from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view

# Vista simple para la ruta principal
@api_view(["GET"])
def api_root(request):
    return Response({"message": "Bienvenido a la API", "endpoints": [
        "/maestros/",
        "/salones/",
        "/estudiantes/",
        "/equipos/",
        "/sesion_juego/  (websockets)"
    ]})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root),  # Ruta principal muestra una respuesta JSON
    path('api-auth/', include('rest_framework.urls')),  # Navegación DRF opcional
    path('maestros/', include('maestros.urls')),
    path('salones/', include('salones.urls')),
    path('estudiantes/', include('estudiantes.urls')),
    path('equipos/', include('equipos.urls')),
]



# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('maestros.urls')),
#     path('', include('salones.urls')),
#     path('', include('estudiantes.urls')),
#     path('', include('equipos.urls')),
#     #path('sesion_juego/', include('sesion_juego.routing')), no se agrega la ruta de web sockets
# ]
