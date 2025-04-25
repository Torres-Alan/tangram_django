from rest_framework import serializers
from evidencias.models import EvidenciaTangram, ImagenEvidencia


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


class EvidenciaTangramSerializer(serializers.ModelSerializer):
    imagenes = ImagenEvidenciaSerializer(many=True, read_only=True)
    actividad_nombre = serializers.CharField(source='actividad.nombre', read_only=True)
    equipo_nombre = serializers.CharField(source='equipo.nombre', read_only=True)

    class Meta:
        model = EvidenciaTangram
        fields = ['id', 'nombre', 'fecha_creacion', 'actividad', 'actividad_nombre', 'equipo', 'equipo_nombre', 'imagenes']