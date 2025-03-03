from django.db import models
from django.utils.timezone import now

from maestros.models import Maestro

# Create your models here.
class Equipos(models.Model):
    nombre = models.CharField(max_length=50)
    created_by = models.ForeignKey(Maestro, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)  # Fecha de creación automática
    #agregar usuarios

    def __str__(self):
        return self.nombre
