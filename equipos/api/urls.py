# equipos/API/urls.py
from django.urls import path
from .views import ActualizarEstadoSesion, EliminarEquipo, EquiposListarVista, ListaEquiposConSesion, ManejoEquipos, ObtenerCodigosPorEquipo

urlpatterns = [
    path('crear_equipo/', ManejoEquipos.as_view(), name='crear_equipo'),
    path('listar_equipos/', EquiposListarVista.as_view(), name='listar_equipos'),  # Ruta para listar los equipos
    path('eliminar_equipo/<int:equipo_id>/', EliminarEquipo.as_view(), name='eliminar_equipo'),
    path('obtener_codigos/<int:equipo_id>/', ObtenerCodigosPorEquipo.as_view(), name='obtener_codigos_por_equipo'),
    path('actualizar_estado_sesion/<int:equipo_id>/', ActualizarEstadoSesion.as_view(), name='actualizar_estado_sesion'),
    path('lista_con_sesion/', ListaEquiposConSesion.as_view(), name='lista_equipos_con_sesion'),

    #path('traer_sesiones_equipo/', ManejoEquipos.as_view(), name='traer_sesiones_equipo'),
]
