# salones/api/views.py
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from salones.models import Salon
from salones.services import RegistrarSalon  # Importar el servicio para crear el salón
from .serializers import SalonSerializer

class SalonCrearVista(APIView):
    def post(self, request):
        try:
            # Los datos enviados desde el frontend (formulario o body JSON)
            serializer = SalonSerializer(data=request.data)

            if serializer.is_valid():
                # Si los datos son válidos, guardamos el salón
                salon = serializer.save()  # Guarda el salón utilizando el serializador

                # Devuelve la respuesta con el ID del salón
                return Response({"id": salon.id, **serializer.data}, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Si hay errores en el serializador, respondemos con 400

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SalonListarVista(APIView):
    def get(self, request):
        try:
            # Usar el usuario autenticado en lugar de pasar el ID del maestro
            maestro = request.user  # Esto obtiene el maestro (usuario autenticado)
            print('maestro en sesión: ',maestro)

            if not maestro.is_authenticated:
                return Response({"error": "No estás autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

            # Filtrar los salones por el maestro autenticado
            salones = Salon.objects.filter(docente=maestro)  # Usamos request.user para obtener el docente

            # Si no existen salones para ese maestro
            if not salones.exists():
                return Response({"error": "No se encontraron salones para este maestro."}, status=status.HTTP_404_NOT_FOUND)

            # Crear la respuesta con los datos de los salones
            salon_data = []
            for salon in salones:
                salon_data.append({
                    "id": salon.id,
                    "grado": salon.grado,
                    "grupo": salon.grupo,
                    "ciclo_escolar_inicio": salon.ciclo_escolar_inicio,
                    "ciclo_escolar_fin": salon.ciclo_escolar_fin,
                    "docente": salon.docente.username,  # O cualquier otro campo relevante
                    "fecha_creacion": salon.fecha_creacion
                })

            return Response(salon_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Ocurrió un error al obtener los salones: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SalonEliminarVista(APIView):
    def delete(self, request, salon_id):
        try:
            salon = Salon.objects.get(id=salon_id)  # Buscar el salón a eliminar

            # Verificar que el maestro autenticado sea el dueño del salón (opcional)
            if request.user != salon.docente:
                return Response({"error": "No tienes permisos para eliminar este salón."}, status=status.HTTP_403_FORBIDDEN)

            salon.delete()  # Eliminar el salón
            return Response({"message": "Salón eliminado con éxito."}, status=status.HTTP_204_NO_CONTENT)

        except Salon.DoesNotExist:
            return Response({"error": "El salón no existe."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Error al eliminar el salón: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
