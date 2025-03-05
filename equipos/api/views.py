# equipos/api/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from equipos.services import CrearEquipo
from django.core.exceptions import ValidationError

class ManejoEquipos(APIView):

    def post(self, request):
        try:
            # Obtener los datos de la solicitud
            data = request.data

            # Verificar los campos requeridos
            campos_requeridos = ["nombre", "salon_id",]  # Verifica si estos campos están presentes
            for campo in campos_requeridos:
                if campo not in data:
                    return Response({"error": f"El campo '{campo}' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

            # Llamar al servicio para crear el equipo
            equipo = CrearEquipo.registrar_equipo(data)

            # Respuesta exitosa
            return Response({"mensaje": f"Equipo '{equipo.nombre}' creado exitosamente."}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
