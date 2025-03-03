# mysite/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('maestros.urls')),  # Las rutas de 'maestros' estarán disponibles en la raíz
    path('', include('salones.urls')),  # Las rutas de 'salones' también estarán disponibles en la raíz
    path('equipos/', include('equipos.urls')),  # Las rutas de 'equipos' también estarán disponibles en la raíz
]
