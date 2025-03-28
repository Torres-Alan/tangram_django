# estudiantes/api/urls.py
from django.urls import path
from .views import EstudianteAsignarEquipo, EstudianteCrearVista, EstudianteEliminarVista, ListarEstudiante, ObtenerIntegrantesEquipo

urlpatterns = [
    path('crear_estudiante/', EstudianteCrearVista.as_view(), name='crear_estudiante'),
    path('agregar_equipo_estudiante/', EstudianteAsignarEquipo.as_view(), name='agregar_equipo_estudiante' ),
    path('listar_estudiantes/', ListarEstudiante.as_view(), name='listar_estudiantes'),
    path('eliminar_alumno/<int:alumno_id>/', EstudianteEliminarVista.as_view(), name='eliminar_alumno'),
    path('obtener_integrantes/', ObtenerIntegrantesEquipo.as_view(), name='obtener_integrantes_equipo'),

]
