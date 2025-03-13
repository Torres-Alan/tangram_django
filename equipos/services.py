# equipos/services.py
from equipos.models import Equipos
from salones.models import Salon
from estudiantes.models import Estudiante
from django.core.exceptions import ValidationError
from maestros.models import Maestro
from sesion_juego.models import SesionJuego

class CrearEquipo:

    @staticmethod
    def registrar_equipo(data):
        """
        Crea un equipo, asigna un maestro y estudiantes del salón.
        """
        # Obtener el nombre del equipo y el ID del maestro
        nombre_equipo = data.get('nombre')
        salon_id = data.get('salon_id')  # ID del salón donde se creará el equipo
        maestros_id = data.get('maestro')

        if not nombre_equipo or not salon_id:
            raise ValidationError("El nombre del equipo y el ID del salón son obligatorios.")

        # Obtener el salón correspondiente
        try:
            salon = Salon.objects.get(id=salon_id)
            print('salon:',salon)
        except Salon.DoesNotExist:
            raise ValidationError(f"El salón con ID {salon_id} no existe.")

        print('maestro:',Maestro.objects.get(id=maestros_id))
        try:
            # Crear el equipo
            equipo = Equipos.objects.create(
                nombre=nombre_equipo,
                created_by=Maestro.objects.get(id=maestros_id),  # El maestro que está creando el equipo (viene en la data)
                salon=salon  # Asociamos el equipo al salón
            )
            #creamos la sesión para el equipo creado
            SesionJuego.objects.create(
                equipo=equipo,
            )
            return {'exito': f'equipo : {equipo} creado '}
        except Exception as e:
            return {'error': f'ocurrio un error {e}'}
