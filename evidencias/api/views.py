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

class EvidenciaCrearVista(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            datos = request.data
            codigo_sesion = datos.get("codigo_sesion")

            from sesion_juego.consumers import estado_sesiones

            # 🛡️ Verifica si ya se creó evidencia en esta sesión
            if codigo_sesion in estado_sesiones and "evidencia_id" in estado_sesiones[codigo_sesion]:
                evidencia_id = estado_sesiones[codigo_sesion]["evidencia_id"]
                evidencia = EvidenciaTangram.objects.get(id=evidencia_id)
                serializer = EvidenciaTangramSerializer(evidencia, context={"request": request})
                return Response({
                    "mensaje": "Ya se registró una evidencia para esta sesión.",
                    "evidencia_id": evidencia.id,
                    "evidencia": serializer.data
                }, status=status.HTTP_200_OK)

            # ✅ Crear nueva evidencia
            evidencia = EvidenciaService.crear_evidencia(datos)

            # 💾 Guardar el ID en memoria para bloquear duplicados
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
            equipo = evidencia.equipo
            salon = actividad.salon if actividad else None

            if salon and salon.docente_id == maestro.id:
                evidencias_data.append({
                    "id": evidencia.id,
                    "nombre": evidencia.nombre,
                    "actividad": actividad.nombre if actividad else "Sin actividad",
                    "salon": f"{salon.grado}° {salon.grupo}" if salon else "Sin salón",
                    "equipo": equipo.nombre if equipo else "Sin equipo",
                    "fecha": evidencia.fecha_creacion.strftime("%Y-%m-%d %H:%M"),
                })

        return Response(evidencias_data)

class InformacionCompletaPorEvidencia(APIView):
    def get(self, request, id_evidencia):
        try:
            evidencia = EvidenciaTangram.objects.select_related('actividad', 'equipo').get(id=id_evidencia)
        except EvidenciaTangram.DoesNotExist:
            return Response({"detail": "La evidencia no existe."}, status=status.HTTP_404_NOT_FOUND)

        imagenes = ImagenEvidencia.objects.filter(evidencia=evidencia).order_by('orden')
        imagenes_serializer = ImagenEvidenciaSerializer(imagenes, many=True, context={'request': request})

        imagenes_originales = evidencia.actividad.banco_tangrams if evidencia.actividad and evidencia.actividad.banco_tangrams else []

        equipo = evidencia.equipo
        estudiantes = Estudiante.objects.filter(equipo=equipo).values('id', 'nombre', 'apellidos', 'nickname')

        equipo_data = {
            "id": equipo.id,
            "nombre": equipo.nombre,
            "salon_id": equipo.salon_id,
            "created_by_id": equipo.created_by_id,
            "created_at": equipo.created_at,
            "estudiantes": list(estudiantes)
        }

        # 🔥 Obtener estadísticas
        estadisticas = EstadisticaEvidencia.objects.filter(evidencia=evidencia)
        estadisticas_serializer = EstadisticaEvidenciaSerializer(estadisticas, many=True)

        # 🔢 Calcular totales
        total_mensajes = sum(e.mensajes_enviados for e in estadisticas)
        total_respuestas = sum(e.respuestas_enviadas for e in estadisticas)
        total_movimientos = sum(e.piezas_movidas for e in estadisticas)

        return Response({
            "evidencia_id": evidencia.id,
            "nombre_evidencia": evidencia.nombre,
            "fecha_creacion": evidencia.fecha_creacion,
            "imagenes_evidencia": imagenes_serializer.data,
            "imagenes_originales": imagenes_originales,
            "equipo": equipo_data,
            "estadisticas": estadisticas_serializer.data,
            "totales": {  # 👈 Sección adicional
                "mensajes_enviados": total_mensajes,
                "respuestas_enviadas": total_respuestas,
                "piezas_movidas": total_movimientos
            }
        }, status=status.HTTP_200_OK)