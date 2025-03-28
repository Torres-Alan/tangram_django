# maestros/API/urls.py
from django.urls import path
from .views import MaestroCrearVista, MaestroAutentificarLogin,CerrarSesionMaestro

urlpatterns = [
    path('crear_maestros/', MaestroCrearVista.as_view(), name='crear_maestro'),
    path('autentificar_maestro/', MaestroAutentificarLogin.as_view(), name='autentificar_maestro'),
    path('cerrar_sesion_maestro/', CerrarSesionMaestro.as_view(), name='cerrar_sesion_maestro'),
]
