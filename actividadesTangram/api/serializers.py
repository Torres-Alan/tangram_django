# actividadesTangram/serializers.py
from rest_framework import serializers
from ..models import Actividad
from salones.models import Salon
from maestros.models import Maestro  # Asegúrate de importar el modelo Maestro

class ActividadSerializer(serializers.ModelSerializer):
    # Este campo es para asociar el salón con la actividad
    salon = serializers.PrimaryKeyRelatedField(queryset=Salon.objects.all(), required=False, allow_null=True)
    # Este campo es para asociar el maestro con la actividad
    maestroId = serializers.PrimaryKeyRelatedField(queryset=Maestro.objects.all(), required=True)

    class Meta:
        model = Actividad
        fields = ['id', 'nombre', 'horas', 'minutos', 'segundos', 'salon', 'banco_tangrams', 'maestroId']
