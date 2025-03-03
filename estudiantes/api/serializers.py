# estudiantes/api/serializers.py
from rest_framework import serializers
from estudiantes.models import Estudiante

class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiante
        fields = ['id', 'nombre', 'apellidos', 'nickname']  # Solo los campos requeridos para Estudiante
