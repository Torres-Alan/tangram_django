# estudiantes/api/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from equipos.models import Equipos
from estudiantes.models import Estudiante
from estudiantes.services import EstudianteService
from estudiantes.api.serializers import EstudianteSerializer
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout

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


class EstudianteAutentificarLogin(APIView):
    def post(self, request):
        try:
            # Obtener el nickname del request
            data = request.data
            nickname = data.get('nickname')

            # Verificar si el nickname existe en la base de datos
            estudiante = Estudiante.objects.filter(nickname=nickname).first()

            if not estudiante:
                # Si no existe el nickname, retornamos un error
                return Response({"error": "El nickname no está registrado."}, status=status.HTTP_400_BAD_REQUEST)

            # Si el nickname existe, se asigna el equipo al estudiante
            equipo = Equipos.objects.filter(salon=estudiante.salon).first()  # Buscar el equipo relacionado con el salón

            if equipo:
                estudiante.equipo = equipo
                estudiante.save()

            # Iniciar sesión con el estudiante (estudiante ya es el usuario)
            login(request, estudiante)  # Inicia la sesión del estudiante (estudiante ya es el usuario)

            return Response({
                "Exito": "Inicio de sesión exitoso.",
                "equipo": equipo.nombre if equipo else "Sin equipo asignado"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EstudianteCerrarSesion(APIView):
    def post(self, request):
        try:
            # Realiza el cierre de sesión
            logout(request)
            return Response({"Exito": "Sesión cerrada correctamente."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Error al cerrar la sesión: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
