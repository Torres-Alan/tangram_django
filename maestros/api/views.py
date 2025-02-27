# maestros/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from maestros.services import registrarMaestro
from ..models import Maestro
from .serializers import MaestroSerializer

class MaestroCrearVista(APIView):
    def post(self, request):
        try:
            # Lista de campos requeridos
            campos_requeridos = ["nombre", "correo", "contrasena"]

            # Obtener los datos de la solicitud
            campos = request.data

            # Verificar si los campos requeridos están presentes en los datos
            for campo in campos_requeridos:
                if campo not in campos:
                    return Response({"error": f"El campo '{campo}' es requerido."}, status=status.HTTP_400_BAD_REQUEST)

            # Si todos los campos requeridos están presentes, devolver éxito
            print(campos)  # Mostrar los datos recibidos (puedes eliminar esta línea si no la necesitas)
            registrarMaestro.crearUsuario(campos, request)
            return Response({"Exito": "Los datos fueron procesados correctamente."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response({"error": "An error occurred, data cannot be processed. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
