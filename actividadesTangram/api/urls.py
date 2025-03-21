from django.urls import path
from .views import ActividadCrearVista, ActividadListarVista  # Importa la vista para crear actividad

urlpatterns = [
    path('crear_actividad/', ActividadCrearVista.as_view(), name='crear_actividad'),
    path('listar_actividad/', ActividadListarVista.as_view(), name='listar_actividades'),
]
