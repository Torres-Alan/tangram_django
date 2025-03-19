# actividadesTangram/api/views.py
from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from actividadesTangram.api.serializers import ActividadSerializer
from actividadesTangram.services import ActividadService

class ActividadCrearVista(APIView):
    def post(self, request):
        try:
            # Usar el servicio para crear la actividad
            actividad = ActividadService.crear_actividad(request.data)

            # Serializar la actividad recién creada
            serializer = ActividadSerializer(actividad)

            # Retornar respuesta con los datos de la actividad
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
