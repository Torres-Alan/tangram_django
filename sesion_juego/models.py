import random
import string
from django.db import models

from equipos.models import Equipos



def generar_codigo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
# Create your models here.
class SesionJuego(models.Model):
    equipo = models.ForeignKey(Equipos, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=10, unique=True, default=generar_codigo)
    creada_en = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)