# equipos/api/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from equipos.models import Equipos
from equipos.services import CrearEquipo
from django.core.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from estudiantes.models import Estudiante
from salones.models import Salon
from sesion_juego.models import SesionJuego

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
            # Obtener el maestro autenticado
            maestro = request.user

            if not maestro.is_authenticated:
                return Response({"error": "No estás autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

            # Obtener el salon_id desde los parámetros de la URL
            salon_id = request.query_params.get("salon_id")
            if not salon_id:
                return Response({"error": "El 'salon_id' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                salon = Salon.objects.get(id=salon_id)
            except Salon.DoesNotExist:
                return Response({"error": "El salón no existe."}, status=status.HTTP_404_NOT_FOUND)

            if salon.docente != maestro:
                return Response({"error": "No tienes permiso para acceder a los equipos de este salón."}, status=status.HTTP_403_FORBIDDEN)

            equipos = Equipos.objects.filter(salon=salon)

            if not equipos.exists():
                return Response({"error": "No hay equipos para este salón."}, status=status.HTTP_404_NOT_FOUND)

            equipos_data = []
            for equipo in equipos:
                # Contar estudiantes asociados al equipo
                cantidad_estudiantes = Estudiante.objects.filter(equipo=equipo).count()

                # Obtener la sesión de juego asociada (si existe)
                sesion = SesionJuego.objects.filter(equipo=equipo).first()

                equipos_data.append({
                    "id": equipo.id,
                    "nombre": equipo.nombre,
                    "created_by": equipo.created_by.username,
                    "created_at": equipo.created_at,
                    "salon": equipo.salon.id,
                    "integrantes": cantidad_estudiantes,
                    "activa": sesion.activa if sesion else False,
                    "codigo": sesion.codigo if sesion else None,
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

class ObtenerCodigosPorEquipo(APIView):
    def get(self, request, equipo_id):
        try:
            # Buscar el equipo por su ID
            equipo = Equipos.objects.get(id=equipo_id)

            # Obtener las sesiones de juego asociadas a ese equipo
            sesiones = SesionJuego.objects.filter(equipo=equipo)

            # Si no existen sesiones para ese equipo
            if not sesiones.exists():
                return Response({"error": "No se encontraron códigos de juego para este equipo."}, status=status.HTTP_404_NOT_FOUND)

            # Crear la respuesta con los datos de las sesiones de juego
            sesiones_data = []
            for sesion in sesiones:
                sesiones_data.append({
                    "id": sesion.id,
                    "codigo": sesion.codigo,
                    "creada_en": sesion.creada_en,
                    "activa": sesion.activa,
                })

            return Response(sesiones_data, status=status.HTTP_200_OK)

        except Equipos.DoesNotExist:
            return Response({"error": "El equipo especificado no existe."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActualizarEstadoSesion(APIView):
    def patch(self, request, equipo_id):
        try:
            # Obtener el estado 'activa' del cuerpo de la solicitud
            activa = request.data.get('activa')
            if activa is None:
                return Response({"error": "El campo 'activa' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

            # Buscar el equipo asociado por equipo_id
            equipo = Equipos.objects.filter(id=equipo_id).first()
            if not equipo:
                return Response({"error": "Equipo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

            # Buscar la sesión de juego asociada con el equipo
            sesion = SesionJuego.objects.filter(equipo=equipo).first()
            if not sesion:
                return Response({"error": "Sesión de juego no encontrada para el equipo."}, status=status.HTTP_404_NOT_FOUND)

            # Obtener el estado actual de la sesión
            estado_actual = sesion.activa

            # Actualizar el estado de 'activa'
            sesion.activa = activa
            sesion.save()

            # Devolver el nuevo estado y el estado anterior
            return Response({
                "message": "Estado de la sesión actualizado correctamente.",
                "estado_anterior": estado_actual,
                "estado_actual": sesion.activa
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Hubo un error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListaEquiposConSesion(APIView):
    def get(self, request):
        try:
            equipos = Equipos.objects.all()
            data = []

            for equipo in equipos:
                sesion = SesionJuego.objects.filter(equipo=equipo).first()
                data.append({
                    "id": equipo.id,
                    "nombre": equipo.nombre,
                    "codigo": sesion.codigo,
                    "activa": sesion.activa if sesion else False
                })

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error al obtener equipos: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#class TraerSesionesEquipo(APIView):