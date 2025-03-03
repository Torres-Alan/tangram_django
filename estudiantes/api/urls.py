# estudiantes/api/urls.py
from django.urls import path
from .views import EstudianteCrearVista  # Importa la vista para crear estudiantes

urlpatterns = [
    path('crear_estudiante/', EstudianteCrearVista.as_view(), name='crear_estudiante'),  # Ruta para crear un estudiante
]
