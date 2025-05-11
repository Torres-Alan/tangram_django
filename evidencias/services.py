from evidencias.models import EvidenciaTangram, ImagenEvidencia, EstadisticaEvidencia
from actividadesTangram.models import Actividad
from equipos.models import Equipos
from estudiantes.models import Estudiante
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
import base64
import uuid

class EvidenciaService:
    @staticmethod
    def crear_evidencia(datos_evidencia):
        """
        Crea una nueva evidencia con sus respectivas imágenes y estadísticas por estudiante.
        """
        try:
            # Validar campos obligatorios
            required_fields = ['actividad_id', 'equipo_id', 'imagenes']
            for field in required_fields:
                if field not in datos_evidencia or not datos_evidencia[field]:
                    raise ValidationError(f"El campo '{field}' es obligatorio.")

            # Obtener la actividad
            try:
                actividad = Actividad.objects.get(id=datos_evidencia['actividad_id'])
            except Actividad.DoesNotExist:
                raise ValidationError("La actividad proporcionada no existe.")

            # Obtener el equipo
            try:
                equipo = Equipos.objects.get(id=datos_evidencia['equipo_id'])
            except Equipos.DoesNotExist:
                raise ValidationError("El equipo proporcionado no existe.")

            # Crear la evidencia
            evidencia = EvidenciaTangram.objects.create(
                actividad=actividad,
                equipo=equipo,
                banco_tangram_original=actividad.banco_tangrams,
                nombre_equipo=equipo.nombre  # o datos_evidencia.get('nombre_equipo') si lo manda el frontend
            )


            # Procesar y guardar imágenes
            imagenes = datos_evidencia['imagenes']  # Lista de strings base64

            for index, img_data in enumerate(imagenes):
                format, imgstr = img_data.split(';base64,')
                ext = format.split('/')[-1]
                nombre_archivo = f"{uuid.uuid4()}.{ext}"
                data = ContentFile(base64.b64decode(imgstr), name=nombre_archivo)

                ImagenEvidencia.objects.create(
                    evidencia=evidencia,
                    imagen=data,
                    orden=index
                )

            # Procesar estadísticas si se incluyen
            estadisticas = datos_evidencia.get('estadisticas', [])
            for estadistica in estadisticas:
                try:
                    estudiante = Estudiante.objects.get(nickname=estadistica['nickname'])
                except Estudiante.DoesNotExist:
                    estudiante = None

                EstadisticaEvidencia.objects.create(
                    evidencia=evidencia,
                    estudiante=estudiante,
                    nombre_estudiante=estadistica.get('nombre_estudiante', ''),
                    nickname_estudiante=estadistica.get('nickname', ''),
                    mensajes_enviados=estadistica.get('mensajes_enviados', 0),
                    respuestas_enviadas=estadistica.get('respuestas_enviadas', 0),
                    piezas_movidas=estadistica.get('piezas_movidas', 0)
                )

            return evidencia

        except ValidationError as ve:
            raise ve
        except Exception as e:
            raise ValidationError(f"Error al crear la evidencia: {str(e)}")