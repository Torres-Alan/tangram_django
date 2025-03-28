# equipos/API/urls.py
from django.urls import path
from .views import EliminarEquipo, EquiposListarVista, ManejoEquipos, ObtenerCodigosPorEquipo

urlpatterns = [
    path('crear_equipo/', ManejoEquipos.as_view(), name='crear_equipo'),
    path('listar_equipos/', EquiposListarVista.as_view(), name='listar_equipos'),  # Ruta para listar los equipos
    path('eliminar_equipo/<int:equipo_id>/', EliminarEquipo.as_view(), name='eliminar_equipo'),
    path('obtener_codigos/<int:equipo_id>/', ObtenerCodigosPorEquipo.as_view(), name='obtener_codigos_por_equipo'),
    #path('traer_sesiones_equipo/', ManejoEquipos.as_view(), name='traer_sesiones_equipo'),
]
