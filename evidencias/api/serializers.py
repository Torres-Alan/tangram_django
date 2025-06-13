from rest_framework import serializers
from django.utils.timezone import localtime
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
    fecha_local = serializers.SerializerMethodField()

    class Meta:
        model = EvidenciaTangram
        fields = [
            'id',
            'nombre',
            'fecha_local',
            'actividad',
            'equipo',
            'nombre_equipo',
            'nombre_actividad',
            'nombre_salon',
            'banco_tangram_original',
            'horas',
            'minutos',
            'segundos',
            'tiempo_asignado_horas',
            'tiempo_asignado_minutos',
            'tiempo_asignado_segundos',
            'imagenes',
            'estadisticas'
        ]

    def get_fecha_local(self, obj):
        return localtime(obj.fecha_creacion).strftime('%d/%m/%Y, %H:%M')