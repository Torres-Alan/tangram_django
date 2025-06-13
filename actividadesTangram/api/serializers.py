from rest_framework import serializers
from ..models import Actividad
from salones.models import Salon
from maestros.models import Maestro

class ActividadSerializer(serializers.ModelSerializer):
    salon = serializers.PrimaryKeyRelatedField(queryset=Salon.objects.all(), required=False, allow_null=True)
    maestroId = serializers.PrimaryKeyRelatedField(queryset=Maestro.objects.all(), required=True)

    class Meta:
        model = Actividad
        fields = ['id', 'nombre', 'horas', 'minutos', 'segundos', 'salon', 'banco_tangrams', 'maestroId', 'activo']
