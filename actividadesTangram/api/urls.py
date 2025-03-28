from django.urls import path
from .views import ActividadCrearVista, ActividadEliminarVista, ActividadListarVista, AsignarSalonActividad  # Importa la vista para crear actividad

urlpatterns = [
    path('crear_actividad/', ActividadCrearVista.as_view(), name='crear_actividad'),
    path('listar_actividad/', ActividadListarVista.as_view(), name='listar_actividades'),
    path('eliminar_actividad/<int:actividad_id>/', ActividadEliminarVista.as_view(), name='eliminar_actividad'),
    path('asignar_salon_actividad/', AsignarSalonActividad.as_view(), name='asignar_salon_actividad'),
]
