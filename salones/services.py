# salones/services.py

from maestros.models import Maestro
from .models import Salon
from rest_framework.response import Response
from rest_framework import status

class RegistrarSalon:
    @staticmethod
    def crearSalon(camposRequeridos, request):
        try:
            # Crear el salón con los datos requeridos
            salon = Salon.objects.create(
                grado=camposRequeridos["grado"],
                grupo=camposRequeridos["grupo"],
                ciclo_escolar_inicio=camposRequeridos["ciclo_escolar_inicio"],
                ciclo_escolar_fin=camposRequeridos["ciclo_escolar_fin"],
                docente=Maestro.objects.get(id=camposRequeridos["docente"])  # Asumimos que el usuario logueado es el docente
            )

            # Guardar el salón
            salon.save()

            return Response({"Exito": "El salón ha sido creado correctamente."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response({"error": "Ocurrió un error al procesar los datos. Por favor, intente nuevamente."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
