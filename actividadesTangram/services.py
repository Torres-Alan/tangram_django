from actividadesTangram.models import Actividad
from salones.models import Salon
from maestros.models import Maestro  # Asegúrate de importar el modelo Maestro
from django.core.exceptions import ValidationError

class ActividadService:
    @staticmethod
    def crear_actividad(datos_actividad):
        """
        Crea una nueva actividad de Tangram con los datos proporcionados.
        """
        try:
            # Validar campos obligatorios
            required_fields = ['nombre', 'horas', 'minutos', 'segundos', 'banco_tangrams', 'maestroId']
            for field in required_fields:
                if field not in datos_actividad or datos_actividad[field] in [None, "", []]:
                    raise ValidationError(f"El campo '{field}' es obligatorio.")

            # Obtener valores de tiempo
            horas = datos_actividad['horas']
            minutos = datos_actividad['minutos']
            segundos = datos_actividad['segundos']

            # Calcular el tiempo total en minutos (por si se usa después)
            tiempo_total_minutos = horas * 60 + minutos + (segundos / 60)

            # Validar banco_tangrams
            banco_tangrams = datos_actividad.get('banco_tangrams', [])
            if not isinstance(banco_tangrams, list):
                raise ValidationError("El campo 'banco_tangrams' debe ser una lista de URLs.")

            # Validar el salón
            salon = None
            if 'salon' in datos_actividad and datos_actividad['salon']:
                try:
                    salon = Salon.objects.get(id=datos_actividad['salon'])
                except Salon.DoesNotExist:
                    raise ValidationError("El salón proporcionado no existe.")

            # Validar el maestroId
            maestro = None
            if 'maestroId' in datos_actividad and datos_actividad['maestroId']:
                try:
                    maestro = Maestro.objects.get(id=datos_actividad['maestroId'])
                except Maestro.DoesNotExist:
                    raise ValidationError("El maestro proporcionado no existe.")
            else:
                raise ValidationError("El campo 'maestroId' es obligatorio.")

            # Crear la actividad
            actividad = Actividad.objects.create(
                nombre=datos_actividad['nombre'],
                horas=horas,
                minutos=minutos,
                segundos=segundos,
                salon=salon,
                banco_tangrams=banco_tangrams,
                maestroId=maestro  # Asociar la actividad con el maestro
            )

            return actividad

        except ValidationError as ve:
            raise ve  # Se vuelve a lanzar para que la vista maneje la excepción
        except Exception as e:
            raise ValidationError(f"Error al crear la actividad: {str(e)}")
