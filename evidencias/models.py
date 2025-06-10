from django.db import models
from django.utils.timezone import now, localtime
from equipos.models import Equipos
from actividadesTangram.models import Actividad
from estudiantes.models import Estudiante


class EvidenciaTangram(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.SET_NULL, null=True, related_name="evidencias")
    equipo = models.ForeignKey(Equipos, on_delete=models.SET_NULL, null=True, related_name="evidencias")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    nombre = models.CharField(max_length=255, editable=False)

    banco_tangram_original = models.JSONField(default=list, blank=True)
    nombre_equipo = models.CharField(max_length=100, blank=True)
    nombre_actividad = models.CharField(max_length=100, blank=True)
    nombre_salon = models.CharField(max_length=100, blank=True)


    horas = models.PositiveIntegerField()
    minutos = models.PositiveIntegerField()
    segundos = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        fecha_hora = localtime().strftime('%Y-%m-%d_%H%M')

        if self.actividad and self.equipo:
            actividad_nombre = self.actividad.nombre.replace(" ", "").strip()[:20]
            equipo_nombre = self.equipo.nombre.replace(" ", "").strip()[:20]

            self.nombre = f"Evidencia_{actividad_nombre}_{equipo_nombre}_{fecha_hora}"

            if not self.nombre_equipo:
                self.nombre_equipo = self.equipo.nombre

            if not self.nombre_actividad:
                self.nombre_actividad = self.actividad.nombre

            if not self.nombre_salon and self.actividad.salon:
                self.nombre_salon = f"{self.actividad.salon.grado} {self.actividad.salon.grupo}"

        else:
            self.nombre = f"Evidencia_SinDatos_{fecha_hora}"

        super().save(*args, **kwargs)


class ImagenEvidencia(models.Model):
    evidencia = models.ForeignKey('EvidenciaTangram', related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='evidencias/')
    orden = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Imagen {self.orden} de {self.evidencia.nombre}"


class EstadisticaEvidencia(models.Model):
    evidencia = models.ForeignKey(EvidenciaTangram, related_name="estadisticas", on_delete=models.CASCADE)

    estudiante = models.ForeignKey(
        Estudiante, on_delete=models.SET_NULL, null=True, blank=True
    )
    nombre_estudiante = models.CharField(max_length=100)
    nickname_estudiante = models.CharField(max_length=50)

    mensajes_enviados = models.PositiveIntegerField(default=0)
    respuestas_enviadas = models.PositiveIntegerField(default=0)
    piezas_movidas = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nickname_estudiante} ({self.nombre_estudiante}) - {self.evidencia.nombre}"