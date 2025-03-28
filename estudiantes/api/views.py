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
from sesion_juego.models import SesionJuego
from rest_framework.permissions import AllowAny

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
            data = request.data
            id_equipo = data.get('id_equipo')  # Obtener el ID del equipo
            equipo = Equipos.objects.get(id=id_equipo)  # Obtener el equipo

            estudiantes_ids = data.get('alumnos', [])
            if not estudiantes_ids:
                return Response({"error": "Se deben proporcionar al menos un estudiante para asignar."}, status=status.HTTP_400_BAD_REQUEST)

            estudiantes = Estudiante.objects.filter(id__in=estudiantes_ids)

            # Detectar cuales estudiantes no están en la base de datos
            estudiantes_no_existentes = [id for id in estudiantes_ids if id not in estudiantes.values_list('id', flat=True)]
            if estudiantes_no_existentes:
                return Response({"error": f"Algunos alumnos no existen: {estudiantes_no_existentes}"}, status=status.HTTP_400_BAD_REQUEST)

            # Filtrar estudiantes que ya tienen un equipo asignado
            estudiantes_con_equipo = estudiantes.filter(equipo__isnull=False)
            if estudiantes_con_equipo.exists():
                estudiantes_con_equipo_ids = estudiantes_con_equipo.values_list('id', flat=True)
                return Response({
                    "error": f"Los siguientes alumnos ya tienen equipo asignado y no pueden ser reasignados: {list(estudiantes_con_equipo_ids)}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Asignar el equipo a todos los estudiantes encontrados
            for estudiante in estudiantes:
                estudiante.equipo = equipo
                estudiante.save()

            return Response({"Exito": f"{len(estudiantes)} estudiantes asignados al equipo '{equipo.nombre}'."}, status=status.HTTP_201_CREATED)

        except Equipos.DoesNotExist:
            return Response({"error": "El equipo especificado no existe."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

class ObtenerIntegrantesEquipo(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            # Obtener el código del equipo enviado en el cuerpo de la solicitud
            codigo = request.data.get("codigo")

            if not codigo:
                return Response({"error": "El código del equipo es requerido."}, status=status.HTTP_400_BAD_REQUEST)

            # Verificar si la sesión de juego existe con ese código
            try:
                sesion = SesionJuego.objects.get(codigo=codigo, activa=True)
            except SesionJuego.DoesNotExist:
                return Response({"error": "Código de equipo inválido o sesión no activa."}, status=status.HTTP_404_NOT_FOUND)

            # Obtener los estudiantes que pertenecen al equipo de esa sesión
            estudiantes = Estudiante.objects.filter(equipo=sesion.equipo)

            # Retornar los estudiantes
            estudiantes_data = [{"id": estudiante.id, "nickname": estudiante.nickname} for estudiante in estudiantes]
            return Response(estudiantes_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
