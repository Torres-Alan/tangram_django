from django.db import models
from salones.models import Salon
from equipos.models import Equipos

class Estudiante(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=200)
    nickname = models.CharField(max_length=100, unique=True)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipos, on_delete=models.SET_NULL, null=True, blank=True)
    last_login = models.DateTimeField(auto_now=True)  # Se actualiza cada vez que el estudiante inicia sesión

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
