# estudiantes/api/serializers.py
from rest_framework import serializers
from estudiantes.models import Estudiante
from salones.api.serializers import SalonSerializer

class EstudianteSerializer(serializers.ModelSerializer):
    salon = SalonSerializer()

    # Hacer el import de EquipoSerializer solo cuando sea necesario
    def to_representation(self, instance):
        # Importar solo aquí para evitar el ciclo
        from equipos.api.serializers import EquipoSerializer
        
        # Llamada al serializador de equipo
        representation = super().to_representation(instance)
        representation['equipo'] = EquipoSerializer(instance.equipo).data if instance.equipo else None
        return representation

    class Meta:
        model = Estudiante
        fields = ['id', 'nombre', 'apellidos', 'nickname', 'salon', 'equipo']
