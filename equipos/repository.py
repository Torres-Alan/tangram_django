

from equipos.models import Equipos


class equipoRepository:
    def crear_equipo(self, nombreEquipo, maestro):
        try:
            print('entra')
            equipo = Equipos.objects.create(nombre=nombreEquipo, created_by=maestro)
            equipo.save()
            return {"mensaje": f"Equipo '{equipo.nombre}' creado exitosamente."}
        except Exception as e:
            return {"error": f"No se pudo crear el equipo: {str(e)}"}