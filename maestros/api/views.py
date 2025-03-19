# maestros/views.py
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from maestros.services import registrarMaestro
from ..models import Maestro
from .serializers import MaestroSerializer
from django.contrib.auth import authenticate, login, logout

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
                    return JsonResponse({"error": f"El campo '{campo}' es requerido."}, status=status.HTTP_400_BAD_REQUEST)

            # Comprobar si ya existe un maestro con el mismo correo (utilizando 'email' en lugar de 'correo')
            if Maestro.objects.filter(email=campos["correo"]).exists():
                return JsonResponse({"error": "Ya existe un maestro con ese correo electrónico."}, status=status.HTTP_400_BAD_REQUEST)

            # Si todos los campos requeridos están presentes y no hay duplicados, registrar el maestro
            registrarMaestro.crearUsuario(campos, request)

            return JsonResponse({"Exito": "Los datos fueron procesados correctamente."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response({"error": "Ocurrió un error, los datos no pueden ser procesados. Inténtelo nuevamente."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MaestroAutentificarLogin(APIView):
    def post(self, request):
        try:
            data = request.data
            correo = data['correo']
            contrasena = data['contrasena']

            # Verifica si el correo existe, si no existe, devuelve un error
            try:
                maestro = Maestro.objects.get(email=correo)  # Busca al maestro por el correo
            except Maestro.DoesNotExist:
                return JsonResponse({"error": "El correo no está registrado."}, status=status.HTTP_400_BAD_REQUEST)

            # Si existe, usa el método authenticate para verificar la contraseña
            maestro_autenticado = authenticate(username=maestro.username, password=contrasena)

            if maestro_autenticado is not None:
                # Si el maestro está autenticado correctamente
                login(request, maestro_autenticado)  # Inicia la sesión

                # Guarda el id del maestro en el request.user
                request.user.id = maestro.id  # Puedes acceder a este `id` más tarde

                return JsonResponse({"Exito": "Los datos fueron procesados correctamente.", "id_maestro": maestro.id}, status=status.HTTP_200_OK)
            else:
                # Si la contraseña no es correcta
                return JsonResponse({"error": "Contraseña incorrecta."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return JsonResponse({"error": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CerrarSesionMaestro(APIView):
    def post(self, request):
        try:
            # Llamamos al método logout para cerrar la sesión
            logout(request)
            return Response({"Exito": "La sesión se cerró correctamente."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "Ocurrió un error al cerrar la sesión."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)