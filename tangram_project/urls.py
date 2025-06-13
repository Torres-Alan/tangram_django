from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from django.conf.urls.static import static


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
    path('', api_root),
    path('api-auth/', include('rest_framework.urls')),
    path('maestros/', include('maestros.urls')),
    path('salones/', include('salones.urls')),
    path('estudiantes/', include('estudiantes.urls')),
    path('equipos/', include('equipos.urls')),
    path('actividades/', include('actividadesTangram.urls')),
    path('evidencias/', include('evidencias.urls')),
    
]


# Para servir archivos multimedia (imágenes de evidencia) en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
