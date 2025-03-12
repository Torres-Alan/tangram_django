# estudiantes/api/urls.py
from django.urls import path
from .views import EstudianteAsignarEquipo, EstudianteCrearVista, EstudianteAutentificarLogin, EstudianteCerrarSesion

urlpatterns = [
    path('crear_estudiante/', EstudianteCrearVista.as_view(), name='crear_estudiante'),
    path('agregar_equipo_estudiante/', EstudianteAsignarEquipo.as_view(), name='agregar_equipo_estudiante' ),
    path('inicio_sesion_estudiante/', EstudianteAutentificarLogin.as_view(), name='inicio_sesion_estudiante'),
    path('cerrar_sesion_estudiante/', EstudianteCerrarSesion.as_view(), name='inicio_sesion_estudiante')

]
