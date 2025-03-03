

from equipos.models import Equipos
from maestros.models import Maestro


class maestroRepository:
    def obtener_maestro_por_id(self,id_maestro):
       try:
           maestro = Maestro.objects.get(id=id_maestro)
           return maestro
       except Exception as e:
           return  {"error": f"No se pudo crear el equipo: {str(e)}"}