# actividadesTangram/api/views.py
from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from actividadesTangram.api.serializers import ActividadSerializer
from actividadesTangram.models import Actividad
from actividadesTangram.services import ActividadService

class ActividadCrearVista(APIView):
    def post(self, request):
        try:
            # Validar si los campos necesarios están presentes en el request
            if 'maestroId' not in request.data:
                return Response({"error": "El campo 'maestroId' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

            # Usar el servicio para crear la actividad
            actividad = ActividadService.crear_actividad(request.data)

            # Serializar la actividad recién creada
            serializer = ActividadSerializer(actividad)

            # Retornar respuesta con los datos de la actividad
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActividadListarVista(APIView):
    def get(self, request):
        try:
            # Usar el usuario autenticado en lugar de pasar el ID del maestro
            maestro = request.user  # Esto obtiene el maestro (usuario autenticado)

            if not maestro.is_authenticated:
                return Response({"error": "No estás autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

            # Filtrar las actividades por el maestro autenticado
            actividades = Actividad.objects.filter(maestroId=maestro)  # Usamos request.user para obtener el maestro

            # Si no existen actividades para ese maestro
            if not actividades.exists():
                return Response({"error": "No se encontraron actividades para este maestro."}, status=status.HTTP_404_NOT_FOUND)

            # Crear la respuesta con los datos de las actividades
            actividad_data = []
            for actividad in actividades:
                actividad_data.append({
                    "id": actividad.id,
                    "nombre": actividad.nombre,
                    "horas": actividad.horas,
                    "minutos": actividad.minutos,
                    "segundos": actividad.segundos,
                    "salon": actividad.salon.id if actividad.salon else None,  # Si el salón es nulo, se pone como None
                    "banco_tangrams": actividad.banco_tangrams,
                    "tiempo_total": actividad.tiempo_total(),
                    "maestro": actividad.maestroId.username,  # O cualquier otro campo relevante
                })

            return Response(actividad_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Ocurrió un error al obtener las actividades: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActividadEliminarVista(APIView):
    def delete(self, request, actividad_id):
        try:
            # Buscar la actividad por su ID
            actividad = Actividad.objects.get(id=actividad_id)
            
            # Eliminar la actividad
            actividad.delete()

            # Responder con éxito
            return Response({"message": "Actividad eliminada correctamente."}, status=status.HTTP_204_NO_CONTENT)

        except Actividad.DoesNotExist:
            # Si la actividad no existe, enviar un error 404
            return Response({"error": "Actividad no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Manejo de cualquier otro error
            return Response({"error": f"Ocurrió un error al eliminar la actividad: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
