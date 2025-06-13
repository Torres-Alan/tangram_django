from django.db import models
from maestros.models import Maestro

class Actividad(models.Model):
    nombre = models.CharField(max_length=255)
    horas = models.PositiveIntegerField()
    minutos = models.PositiveIntegerField()
    segundos = models.PositiveIntegerField()
    salon = models.ForeignKey('salones.Salon', on_delete=models.SET_NULL, null=True, blank=True)
    banco_tangrams = models.JSONField()  # Aquí se almacenan las URLs de imágenes
    maestroId = models.ForeignKey(Maestro, on_delete=models.CASCADE)
    activo = models.BooleanField(default=False)

    def tiempo_total(self):
        return self.horas * 60 + self.minutos + self.segundos / 60

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Actividad Tangram"
        verbose_name_plural = "Actividades Tangram"