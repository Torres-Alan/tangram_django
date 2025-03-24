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
from salones.models import Salon

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


class ListarEstudiante(APIView):
    def get(self, request):
        try:
            # Obtener el maestro autenticado (request.user)
            maestro = request.user

            # Verificar si el maestro está autenticado
            if not maestro.is_authenticated:
                return Response({"error": "No estás autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

            # Obtener el salon_id desde los parámetros de la URL
            salon_id = request.query_params.get("salon_id")  # Usamos query_params para obtener parámetros de la URL

            if not salon_id:
                return Response({"error": "El 'salon_id' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Obtener el salón correspondiente con el salon_id
                salon = Salon.objects.get(id=salon_id)
            except Salon.DoesNotExist:
                return Response({"error": "El salón no existe."}, status=status.HTTP_404_NOT_FOUND)

            # Verificar si el maestro tiene acceso a ese salón
            if salon.docente != maestro:
                return Response({"error": "No tienes permiso para acceder a los estudiantes de este salón."}, status=status.HTTP_403_FORBIDDEN)

            # Filtrar los estudiantes del salón del maestro
            estudiantes = Estudiante.objects.filter(salon=salon)

            # Si no hay estudiantes en ese salón
            if not estudiantes.exists():
                return Response({"error": "No hay estudiantes en este salón."}, status=status.HTTP_404_NOT_FOUND)

            # Crear la respuesta con los datos de los estudiantes
            estudiantes_data = []
            for estudiante in estudiantes:
                estudiantes_data.append({
                    "id": estudiante.id,
                    "nombre": estudiante.nombre,
                    "apellidos": estudiante.apellidos,
                    "nickname": estudiante.nickname,
                    "salon": estudiante.salon.id,
                    "equipo": estudiante.equipo.id if estudiante.equipo else None,
                })

            return Response(estudiantes_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Ocurrió un error al obtener los estudiantes: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EstudianteEliminarVista(APIView):
    def delete(self, request, alumno_id):
        try:
            # Buscar el alumno por su ID
            alumno = Estudiante.objects.get(id=alumno_id)

            # Eliminar el alumno
            alumno.delete()

            # Responder con éxito
            return Response({"message": "Alumno eliminado correctamente."}, status=status.HTTP_204_NO_CONTENT)

        except Estudiante.DoesNotExist:
            # Si el alumno no existe, enviar un error 404
            return Response({"error": "Alumno no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Manejo de cualquier otro error
            return Response({"error": f"Ocurrió un error al eliminar el alumno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
