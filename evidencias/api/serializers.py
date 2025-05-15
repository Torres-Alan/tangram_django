from rest_framework import serializers
from evidencias.models import EvidenciaTangram, ImagenEvidencia, EstadisticaEvidencia


class ImagenEvidenciaSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = ImagenEvidencia
        fields = ['id', 'orden', 'imagen_url']

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and hasattr(obj.imagen, 'url'):
            return request.build_absolute_uri(obj.imagen.url) if request else obj.imagen.url
        return None


class EstadisticaEvidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadisticaEvidencia
        fields = [
            'id',
            'nombre_estudiante',
            'nickname_estudiante',
            'mensajes_enviados',
            'respuestas_enviadas',
            'piezas_movidas'
        ]

class EvidenciaTangramSerializer(serializers.ModelSerializer):
    imagenes = ImagenEvidenciaSerializer(many=True, read_only=True)
    estadisticas = EstadisticaEvidenciaSerializer(many=True, read_only=True)

    class Meta:
        model = EvidenciaTangram
        fields = [
            'id',
            'nombre',
            'fecha_creacion',
            'actividad',
            'equipo',
            'nombre_equipo',
            'nombre_actividad',
            'nombre_salon',
            'banco_tangram_original',
            'imagenes',
            'estadisticas'
        ]