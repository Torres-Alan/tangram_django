from django.urls import path
from .views import EvidenciaCrearVista, EvidenciaEliminarVista, EvidenciasDelMaestroView, InformacionCompletaPorEvidencia

urlpatterns = [
    path('crear_evidencia/', EvidenciaCrearVista.as_view(), name='crear_evidencia'),
    path('listar_evidencias/', EvidenciasDelMaestroView.as_view(), name='listar_evidencias'),
    path('informacion_completa_evidencia/<int:id_evidencia>/', InformacionCompletaPorEvidencia.as_view(), name='informacion_completa_evidencia'),
    path('eliminar_evidencia/<int:evidencia_id>/', EvidenciaEliminarVista.as_view(), name='eliminar_evidencia'),
]
