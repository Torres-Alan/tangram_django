#Un serializador es necesario para convertir tus datos de modelos de Django a un formato JSON (y viceversa). Vamos a crear un serializador para tu modelo Maestro.
# maestros/serializers.py
from rest_framework import serializers
from ..models import Maestro

class MaestroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maestro
        fields = ['id', 'username', 'email', 'fecha_creacion']  # Campos a incluir en la API
