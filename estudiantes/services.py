# estudiantes/services.py
from estudiantes.models import Estudiante
from salones.models import Salon
from equipos.models import Equipos  # Importamos Equipos
from django.core.exceptions import ValidationError

class EstudianteService:

    @staticmethod
    def crear_estudiante(datos_estudiante):
        """
        Crea un estudiante con nombre, apellidos, nickname, salón y equipo.
        """
        # Verificar que los datos necesarios están presentes
        required_fields = ['nombre', 'apellidos', 'nickname', 'salon_id']  # Requiere equipo también
        for field in required_fields:
            if field not in datos_estudiante:
                raise ValidationError(f"El campo '{field}' es obligatorio.")

        # Obtener el salón correspondiente
        try:
            salon = Salon.objects.get(id=datos_estudiante['salon_id'])
        except Salon.DoesNotExist:
            raise ValidationError("El salón especificado no existe.")
        # Crear el estudiante
        estudiante = Estudiante.objects.create(
            nombre=datos_estudiante['nombre'],
            apellidos=datos_estudiante['apellidos'],
            nickname=datos_estudiante['nickname'],
            salon=salon,
        )

        return estudiante
