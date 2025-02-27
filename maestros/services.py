from rest_framework import status
from maestros.models import Maestro
from rest_framework.response import Response

class registrarMaestro:
    def crearUsuario(camposRequeridos, request):
        # Crea un nuevo usuario con los campos requeridos
        try:
            maestro = Maestro.objects.create_user(username=camposRequeridos["nombre"], email=camposRequeridos["correo"], password=camposRequeridos["contrasena"])
            return Response({"Se creo el maestro."})

        except Exception as e:
            return Response({"error": "An error occurred, data cannot be processed. please try again"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)