# equipos/api/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from equipos.models import Equipos
from equipos.services import CrearEquipo
from django.core.exceptions import ValidationError

from salones.models import Salon

class ManejoEquipos(APIView):

    def post(self, request):
        try:
            # Obtener los datos de la solicitud
            data = request.data

            # Verificar los campos requeridos
            campos_requeridos = ["nombre_equipo", "salon_id",]  # Verifica si estos campos están presentes
            for campo in campos_requeridos:
                if campo not in data:
                    return Response({"error": f"El campo '{campo}' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

            # Llamar al servicio para crear el equipo
            equipo = CrearEquipo.registrar_equipo(data)
            print(equipo)

            if 'exito' in equipo:
                return Response({"mensaje": f"Equipo '{equipo}' creado exitosamente."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"mensaje": f"Equipo '{equipo}' no creado exitosamente."}, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EquiposListarVista(APIView):
    def get(self, request):
        try:
            # Obtener el maestro autenticado (request.user)
            maestro = request.user

            # Verificar si el maestro está autenticado
            if not maestro.is_authenticated:
                return Response({"error": "No estás autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

            # Obtener el salon_id desde los parámetros de la URL
            salon_id = request.query_params.get("salon_id")

            if not salon_id:
                return Response({"error": "El 'salon_id' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Obtener el salón correspondiente con el salon_id
                salon = Salon.objects.get(id=salon_id)
            except Salon.DoesNotExist:
                return Response({"error": "El salón no existe."}, status=status.HTTP_404_NOT_FOUND)

            # Verificar si el maestro tiene acceso a ese salón
            if salon.docente != maestro:
                return Response({"error": "No tienes permiso para acceder a los equipos de este salón."}, status=status.HTTP_403_FORBIDDEN)

            # Filtrar los equipos del salón
            equipos = Equipos.objects.filter(salon=salon)

            # Si no hay equipos en ese salón
            if not equipos.exists():
                return Response({"error": "No hay equipos para este salón."}, status=status.HTTP_404_NOT_FOUND)

            # Crear la respuesta con los datos de los equipos
            equipos_data = []
            for equipo in equipos:
                equipos_data.append({
                    "id": equipo.id,
                    "nombre": equipo.nombre,
                    "created_by": equipo.created_by.username,  # Nombre del maestro que creó el equipo
                    "created_at": equipo.created_at,
                    "salon": equipo.salon.id,
                })

            return Response(equipos_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Ocurrió un error al obtener los equipos: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EliminarEquipo(APIView):
    def delete(self, request, equipo_id):
        try:
            # Verificar si el equipo existe
            equipo = Equipos.objects.get(id=equipo_id)

            # Eliminar el equipo
            equipo.delete()

            return Response({"Exito": f"El equipo '{equipo.nombre}' ha sido eliminado correctamente."}, status=status.HTTP_204_NO_CONTENT)

        except Equipos.DoesNotExist:
            return Response({"error": "El equipo especificado no existe."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#class TraerSesionesEquipo(APIView):