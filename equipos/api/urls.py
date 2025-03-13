# equipos/API/urls.py
from django.urls import path
from .views import ManejoEquipos

urlpatterns = [
    path('crear_equipo/', ManejoEquipos.as_view(), name='crear_equipo'),
    #path('traer_sesiones_equipo/', ManejoEquipos.as_view(), name='traer_sesiones_equipo'),
]
