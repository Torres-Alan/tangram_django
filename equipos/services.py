

from equipos.repository import equipoRepository
from maestros.repositoy import maestroRepository


class crearEquipo:
    def registrarEquipo(request, data):
        try:
            # Verificar si 'nombre' está en data
            nombreEquipo = data.get('nombre')
            maestroRepo=maestroRepository()
            maestro= maestroRepo.obtener_maestro_por_id(data.get('id_maestro'))
            if not nombreEquipo and not maestro:
                return {"error": "El nombre del equipo es obligatorio."}, 400  # Código HTTP 400 (Bad Request)

            # Crear el repositorio e intentar registrar el equipo
            repository = equipoRepository()
            response=repository.crear_equipo(nombreEquipo,maestro)
            print(response)
            return {"mensaje": f"Equipo '{response}' creado exitosamente."}, 201  # Código HTTP 201 (Created)
        except Exception as e:
            return {"error": f"Ocurrió un error inesperado: {str(e)}"}, 500  # Código HTTP 500 (Internal Server Error)