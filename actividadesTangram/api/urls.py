from django.urls import path
from .views import ActividadCrearVista  # Importa la vista para crear actividad

urlpatterns = [
    path('crear_actividad/', ActividadCrearVista.as_view(), name='crear_actividad'),
]
