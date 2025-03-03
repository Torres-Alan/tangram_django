# equipos/API/urls.py
from django.urls import path
from .views import manejoEquipos  # Asegúrate de importar las vistas adecuadas

urlpatterns = [
    path('crear_equipo/', manejoEquipos.as_view(), name='crear_equipo'),  # Ruta para crear un maestro
]
