# salones/models.py
from django.db import models
from maestros.models import Maestro  # Relacionar con el modelo de Maestro

class Salon(models.Model):
    GRADOS = [(i, str(i)) for i in range(1, 7)]  # Grados 1-6
    GRUPOS = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]  # Grupos A, B, C, D

    grado = models.IntegerField(choices=GRADOS)  # Grado 1-6
    grupo = models.CharField(max_length=1, choices=GRUPOS)  # Grupo A-D
    ciclo_escolar_inicio = models.PositiveIntegerField()  # Año de inicio del ciclo escolar
    ciclo_escolar_fin = models.PositiveIntegerField()  # Año de fin del ciclo escolar
    docente = models.ForeignKey(Maestro, on_delete=models.CASCADE)  # Relación con el maestro
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación del salón
    nombre = models.CharField(max_length=100, blank=True, null=True)  # Campo para almacenar el nombre generado

    def __str__(self):
        return self.nombre  # Usar el nombre generado como representación del salón

    def save(self, *args, **kwargs):
        if not self.nombre:  # Si no hay nombre (es decir, el maestro no lo proporcionó)
            # Generar un nombre automático basado en los valores de grado, grupo y ciclo escolar
            self.nombre = f"Grado {self.grado} - Grupo {self.grupo} ({self.ciclo_escolar_inicio}-{self.ciclo_escolar_fin})"
        super(Salon, self).save(*args, **kwargs)  # Llamar al método save original

    class Meta:
        verbose_name = "Salón"
        verbose_name_plural = "Salones"
