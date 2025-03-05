# equipos/api/serializers.py
from rest_framework import serializers
from equipos.models import Equipos
from estudiantes.api.serializers import EstudianteSerializer  # Importa el serializador de Estudiante

class EquipoSerializer(serializers.ModelSerializer):
    estudiantes = EstudianteSerializer(many=True)  # Incluye los estudiantes en la creación del equipo

    class Meta:
        model = Equipos
        fields = ['id', 'nombre', 'salon',]
