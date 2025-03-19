# actividadesTangram/serializers.py
from rest_framework import serializers
from ..models import Actividad

class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = ['id', 'nombre', 'horas', 'minutos', 'segundos', 'salon', 'banco_tangrams']
