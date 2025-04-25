from django.urls import path
from .views import EvidenciaCrearVista

urlpatterns = [
    path('crear_evidencia/', EvidenciaCrearVista.as_view(), name='crear_evidencia')
]
