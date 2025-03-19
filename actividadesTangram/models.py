# actividadesTangram/models.py
from django.db import models

class Actividad(models.Model):
    nombre = models.CharField(max_length=255)
    horas = models.PositiveIntegerField()  # Campo para horas
    minutos = models.PositiveIntegerField()  # Campo para minutos
    segundos = models.PositiveIntegerField()  # Campo para segundos
    salon = models.ForeignKey('salones.Salon', on_delete=models.SET_NULL, null=True, blank=True)
    banco_tangrams = models.JSONField()

    def tiempo_total(self):
        # Esto devuelve el tiempo total en minutos, tomando en cuenta horas, minutos y segundos
        return self.horas * 60 + self.minutos + self.segundos / 60

    def __str__(self):
        return self.nombre
