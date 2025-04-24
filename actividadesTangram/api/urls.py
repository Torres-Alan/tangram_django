from django.urls import path
from .views import ActivarActividad, ActividadActivaPorEquipo, ActividadCrearVista, ActividadEliminarVista, ActividadListarVista, AsignarSalonActividad
urlpatterns = [
    path('crear_actividad/', ActividadCrearVista.as_view(), name='crear_actividad'),
    path('listar_actividad/', ActividadListarVista.as_view(), name='listar_actividades'),
    path('eliminar_actividad/<int:actividad_id>/', ActividadEliminarVista.as_view(), name='eliminar_actividad'),
    path('asignar_salon_actividad/', AsignarSalonActividad.as_view(), name='asignar_salon_actividad'),
    path('activar_actividad/<int:actividad_id>/', ActivarActividad.as_view(), name='activar_actividad'),
    path('actividad_activa_por_equipo/<str:codigo_equipo>/', ActividadActivaPorEquipo.as_view(), name='actividad_activa_por_equipo'),

]
