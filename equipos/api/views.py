# maestros/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from equipos.services import crearEquipo


class manejoEquipos(APIView):
    def post(self, request):
        try:
            print('entra')
            # Lista de campos requeridos
            campos_requeridos = ["nombre", "id_maestro"]

            # Obtener los datos de la solicitud
            campos = request.data
            # Verificar si los campos requeridos están presentes en los datos
            for campo in campos_requeridos:
                if campo not in campos:
                    return Response({"error": f"El campo '{campo}' es requerido."}, status=status.HTTP_400_BAD_REQUEST)

            #mandar al service a crear el equipo
            response=crearEquipo.registrarEquipo(request, campos)
            return Response(response, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response({"error": f"Ocurrió un error, los datos no pueden ser procesados. Inténtelo nuevamente. {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
