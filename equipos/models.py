# equipos/models.py
from django.db import models
from django.utils.timezone import now
from maestros.models import Maestro
from salones.models import Salon  # Relacionar con el modelo Salon

class Equipos(models.Model):
    nombre = models.CharField(max_length=50)
    created_by = models.ForeignKey(Maestro, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
