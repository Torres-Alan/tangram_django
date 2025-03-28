from django.db import models
from maestros.models import Maestro  # Asegúrate de importar el modelo Maestro

class Actividad(models.Model):
    nombre = models.CharField(max_length=255)
    horas = models.PositiveIntegerField()  # Campo para horas
    minutos = models.PositiveIntegerField()  # Campo para minutos
    segundos = models.PositiveIntegerField()  # Campo para segundos
    salon = models.ForeignKey('salones.Salon', on_delete=models.SET_NULL, null=True, blank=True)
    banco_tangrams = models.JSONField()
    maestroId = models.ForeignKey(Maestro, on_delete=models.CASCADE)  # Relación con el maestro

    def tiempo_total(self):
        # Esto devuelve el tiempo total en minutos, tomando en cuenta horas, minutos y segundos
        return self.horas * 60 + self.minutos + self.segundos / 60

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Actividad Tangram"
        verbose_name_plural = "Actividades Tangram"
