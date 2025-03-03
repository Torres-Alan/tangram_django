# estudiantes/api/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from estudiantes.services import EstudianteService
from estudiantes.api.serializers import EstudianteSerializer
from django.core.exceptions import ValidationError  # Importar desde django.core.exceptions

class EstudianteCrearVista(APIView):
    def post(self, request):
        try:
            # Obtener los datos del estudiante
            datos_estudiante = request.data

            # Usar el servicio para crear el estudiante
            estudiante = EstudianteService.crear_estudiante(datos_estudiante)

            # Serializar el estudiante para la respuesta
            serializer = EstudianteSerializer(estudiante)

            # Retornar la respuesta exitosa
            return Response({"Exito": "Estudiante creado con éxito.", "estudiante": serializer.data}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado.{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



