from django.urls import path
from .views import SalonCrearVista, SalonEditarVista, SalonEliminarVista, SalonListarVista

urlpatterns = [
    path('crear_salones/', SalonCrearVista.as_view(), name='crear_salones'),
    path('listar_salon/', SalonListarVista.as_view(), name='listar_salon'),
    path('editar_salon/<int:salon_id>/', SalonEditarVista.as_view(), name='editar_salon'),
    path('eliminar_salon/<int:salon_id>/', SalonEliminarVista.as_view(), name='eliminar_salon'),
]