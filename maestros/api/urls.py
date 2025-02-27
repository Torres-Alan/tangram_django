# maestros/API/urls.py
from django.urls import path
from .views import MaestroCrearVista  # Asegúrate de importar las vistas adecuadas

urlpatterns = [
    path('crear_maestros/', MaestroCrearVista.as_view(), name='crear_maestro'),  # Ruta para crear un maestro
]
