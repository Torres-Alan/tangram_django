# salones/serializers.py
from rest_framework import serializers
from ..models import Salon

class SalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = ['id', 'grado', 'grupo', 'ciclo_escolar_inicio', 'ciclo_escolar_fin', 'docente', 'fecha_creacion']  # Campos a incluir en la API
