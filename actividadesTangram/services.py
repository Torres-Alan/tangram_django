from actividadesTangram.models import Actividad
from salones.models import Salon
from django.core.exceptions import ValidationError

class ActividadService:
    @staticmethod
    def crear_actividad(datos_actividad):
        """
        Crea una nueva actividad de Tangram con los datos proporcionados.
        """
        try:
            # Verificar que los datos necesarios están presentes
            required_fields = ['nombre', 'horas', 'minutos', 'segundos', 'banco_tangrams']
            for field in required_fields:
                if field not in datos_actividad:
                    raise ValidationError(f"El campo '{field}' es obligatorio.")

            # Obtener los valores de tiempo
            horas = datos_actividad['horas']
            minutos = datos_actividad['minutos']
            segundos = datos_actividad['segundos']

            # Calcular el tiempo total en minutos
            tiempo_total_minutos = horas * 60 + minutos + (segundos / 60)

            # Obtener el salón si se proporciona
            salon = None
            if 'salon' in datos_actividad:
                try:
                    salon = Salon.objects.get(id=datos_actividad['salon'])
                except Salon.DoesNotExist:
                    raise ValidationError("El salón proporcionado no existe.")

            # Crear la actividad de Tangram
            actividad = Actividad.objects.create(
                nombre=datos_actividad['nombre'],
                horas=horas,
                minutos=minutos,
                segundos=segundos,
                salon=salon,
                banco_tangrams=datos_actividad['banco_tangrams']
            )

            return actividad

        except ValidationError as ve:
            raise ve  # Se vuelve a lanzar para que la vista maneje la excepción
        except Exception as e:
            raise ValidationError(f"Error al crear la actividad: {str(e)}")

