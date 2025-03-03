# salones/api/urls.py
from django.urls import path
from .views import SalonCrearVista

urlpatterns = [
    path('crear_salones/', SalonCrearVista.as_view(), name='crear_salon'),
]
