from django.urls import path
from .views import SalonCrearVista, SalonListarVista  # Importar las vistas para crear y listar salones

urlpatterns = [
    path('crear_salones/', SalonCrearVista.as_view(), name='crear_salones'),  # Endpoint para crear un salón
    path('listar_salon/', SalonListarVista.as_view(), name='listar_salon'),  # Endpoint para listar los salones
]
