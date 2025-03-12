# estudiantes/api/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from equipos.models import Equipos
from estudiantes.models import Estudiante
from estudiantes.services import EstudianteService
from estudiantes.api.serializers import EstudianteSerializer
from django.core.exceptions import ValidationError

class EstudianteCrearVista(APIView):
    def post(self, request):
        try:
            # Usar el servicio para crear el estudiante con el equipo y salón
            estudiante = EstudianteService.crear_estudiante(request.data)

            # Serializar la respuesta
            serializer = EstudianteSerializer(estudiante)

            return Response({"Exito": "Estudiante creado con éxito.", "estudiante": serializer.data}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado.{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EstudianteAsignarEquipo(APIView):
    def post(self, request):
        try:
            # Recibir los datos de la solicitud
            data = request.data
            id_equipo = data.get('id_equipo')
            equipo = Equipos.objects.get(id=id_equipo)  # Obtener el equipo

            # Verificar si 'id_estudiantes' está en la solicitud (ahora esperamos una lista de IDs de estudiantes)
            estudiantes_ids = data.get('id_estudiantes', [])
            if not estudiantes_ids:
                return Response({"error": "Se deben proporcionar al menos un estudiante para asignar."}, status=status.HTTP_400_BAD_REQUEST)

            estudiantes = Estudiante.objects.filter(id__in=estudiantes_ids)  # Filtramos los estudiantes por los IDs proporcionados

            # Asignar el equipo a todos los estudiantes seleccionados
            for estudiante in estudiantes:
                estudiante.equipo = equipo
                estudiante.save()

            return Response({"Exito": f"{len(estudiantes)} estudiantes asignados al equipo '{equipo.nombre}'."}, status=status.HTTP_201_CREATED)

        except Equipos.DoesNotExist:
            return Response({"error": "El equipo especificado no existe."}, status=status.HTTP_400_BAD_REQUEST)
        except Estudiante.DoesNotExist:
            return Response({"error": "Uno o más estudiantes no existen."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)