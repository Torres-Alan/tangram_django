# estudiantes/models.py
from django.db import models

class Estudiante(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=200)
    nickname = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
