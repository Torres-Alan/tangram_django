from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from estudiantes.models import Estudiante
from evidencias.models import EstadisticaEvidencia, EvidenciaTangram, ImagenEvidencia
from evidencias.services import EvidenciaService
from evidencias.api.serializers import EstadisticaEvidenciaSerializer, EvidenciaTangramSerializer, ImagenEvidenciaSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import localtime

class EvidenciaCrearVista(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            datos = request.data
            evidencia = EvidenciaService.crear_evidencia(datos)

            # Guardar evidencia_id en estado_sesiones
            from sesion_juego.consumers import estado_sesiones
            codigo_sesion = datos.get("codigo_sesion")
            if codigo_sesion:
                if codigo_sesion not in estado_sesiones:
                    estado_sesiones[codigo_sesion] = {}
                estado_sesiones[codigo_sesion]["evidencia_id"] = evidencia.id

            serializer = EvidenciaTangramSerializer(evidencia, context={"request": request})
            return Response({
                "evidencia_id": evidencia.id,
                "evidencia": serializer.data
            }, status=status.HTTP_201_CREATED)

        except ValidationError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EvidenciasDelMaestroView(APIView):
    def get(self, request):
        maestro = request.user
        actividad_id = request.query_params.get('actividad')
        salon_id = request.query_params.get('salon')
        equipo_id = request.query_params.get('equipo')

        evidencias_data = []

        evidencias = EvidenciaTangram.objects.select_related(
            "actividad", "equipo", "actividad__salon"
        ).all()

        # Filtros
        if actividad_id:
            evidencias = evidencias.filter(actividad__id=actividad_id)
        if salon_id:
            evidencias = evidencias.filter(actividad__salon__id=salon_id)
        if equipo_id:
            evidencias = evidencias.filter(equipo__id=equipo_id)

        for evidencia in evidencias:
            actividad = evidencia.actividad
            salon = actividad.salon if actividad else None

            # Si no hay actividad ni salón, permitir igualmente mostrar la evidencia
            if not actividad or (salon and salon.docente_id == maestro.id):
                evidencias_data.append({
                    "id": evidencia.id,
                    "nombre": evidencia.nombre,
                    "actividad": evidencia.nombre_actividad if evidencia.nombre_actividad else "Sin actividad",
                    "salon": evidencia.nombre_salon if evidencia.nombre_salon else "Sin salón",
                    "equipo": evidencia.nombre_equipo if evidencia.nombre_equipo else "Sin equipo",
                    "fecha": localtime(evidencia.fecha_creacion).strftime("%Y-%m-%d %H:%M"),
                })

        return Response(evidencias_data)

class InformacionCompletaPorEvidencia(APIView):
    def get(self, request, id_evidencia):
        try:
            evidencia = EvidenciaTangram.objects.select_related('actividad', 'equipo').get(id=id_evidencia)
        except EvidenciaTangram.DoesNotExist:
            return Response({"detail": "La evidencia no existe."}, status=status.HTTP_404_NOT_FOUND)

        # Imágenes de evidencia (con índice)
        imagenes = ImagenEvidencia.objects.filter(evidencia=evidencia).order_by('orden')
        imagenes_serializer = ImagenEvidenciaSerializer(imagenes, many=True, context={'request': request})
        imagenes_con_indice = [
            {**img, "indice": img.get("orden", 0)} for img in imagenes_serializer.data
        ]

        # Imágenes originales de la actividad
        imagenes_originales = evidencia.banco_tangram_original or []

        # Estadísticas asociadas
        estadisticas = EstadisticaEvidencia.objects.filter(evidencia=evidencia)
        estadisticas_serializer = EstadisticaEvidenciaSerializer(estadisticas, many=True)

        # Totales
        total_mensajes = sum(e.mensajes_enviados for e in estadisticas)
        total_respuestas = sum(e.respuestas_enviadas for e in estadisticas)
        total_movimientos = sum(e.piezas_movidas for e in estadisticas)

        return Response({
            "evidencia_id": evidencia.id,
            "nombre_evidencia": evidencia.nombre,
            "nombre_actividad": evidencia.nombre_actividad,
            "nombre_salon": evidencia.nombre_salon,
            "nombre_equipo": evidencia.nombre_equipo,
            "fecha_creacion": evidencia.fecha_creacion,
            "imagenes_evidencia": imagenes_con_indice,
            "imagenes_originales": imagenes_originales,
            "estadisticas": estadisticas_serializer.data,
            "estudiantes_registrados": [
                {
                    "nombre_estudiante": est.nombre_estudiante,
                    "nickname_estudiante": est.nickname_estudiante
                }
                for est in estadisticas
            ],
            "totales": {
                "mensajes_enviados": total_mensajes,
                "respuestas_enviadas": total_respuestas,
                "piezas_movidas": total_movimientos
            },
            "duracion_usada": {
                "horas": evidencia.horas,
                "minutos": evidencia.minutos,
                "segundos": evidencia.segundos
            },
            "duracion_asignada": {
                "horas": evidencia.tiempo_asignado_horas,
                "minutos": evidencia.tiempo_asignado_minutos,
                "segundos": evidencia.tiempo_asignado_segundos
            }
        }, status=status.HTTP_200_OK)


class EvidenciaEliminarVista(APIView):
    def delete(self, request, evidencia_id):
        try:
            evidencia = get_object_or_404(EvidenciaTangram, id=evidencia_id)

            evidencia.delete()

            return Response({"message": "Evidencia eliminada correctamente."}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({"error": f"Ocurrió un error al eliminar la evidencia: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)