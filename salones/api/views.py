# salones/api/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from salones.services import RegistrarSalon  # Importar el servicio para crear el salón
from .serializers import SalonSerializer

class SalonCrearVista(APIView):
    def post(self, request):
        try:
            # Los datos enviados desde el frontend (formulario o body JSON)
            serializer = SalonSerializer(data=request.data)

            if serializer.is_valid():
                # Si los datos son válidos, llamamos al servicio para crear el salón
                return RegistrarSalon.crearSalon(request.data, request)  # Usamos el servicio que delega la creación

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Si hay errores en el serializador, respondemos con 400

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
