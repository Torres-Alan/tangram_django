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
            data=request.data
            id_equipo=data.get('id_equipo')
            equipo=Equipos.objects.get(id=id_equipo)
            id_estudiante=data.get('id_estudiante')
            estudiante=Estudiante.objects.get(id=id_estudiante)
            estudiante.equipo=equipo
            estudiante.save()
            return Response({"Exito": "Equipo asignado con éxito."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado.{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
