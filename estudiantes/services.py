# estudiantes/services.py
from estudiantes.models import Estudiante
from django.core.exceptions import ValidationError

class EstudianteService:

    @staticmethod
    def crear_estudiante(datos_estudiante):
        """
        Crea un estudiante con nombre, apellidos y nickname.
        """
        # Verificar que los datos necesarios están presentes
        required_fields = ['nombre', 'apellidos', 'nickname']
        for field in required_fields:
            if field not in datos_estudiante:
                raise ValidationError(f"El campo '{field}' es obligatorio.")

        # Crear el estudiante
        estudiante = Estudiante.objects.create(
            nombre=datos_estudiante['nombre'],
            apellidos=datos_estudiante['apellidos'],
            nickname=datos_estudiante['nickname']
        )

        return estudiante
