from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from evidencias.services import EvidenciaService
from evidencias.api.serializers import EvidenciaTangramSerializer

class EvidenciaCrearVista(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            datos = request.data
            evidencia = EvidenciaService.crear_evidencia(datos)

            serializer = EvidenciaTangramSerializer(evidencia, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)