# mysite/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('maestros.urls')),
    path('', include('salones.urls')),
    path('', include('estudiantes.urls')),
    path('equipos/', include('equipos.urls')),  # Las rutas de 'equipos' también estarán disponibles en la raíz
]
