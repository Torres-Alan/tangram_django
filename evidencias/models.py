from django.db import models
from django.utils.timezone import now, localtime

# Importaciones necesarias
from equipos.models import Equipos
from actividadesTangram.models import Actividad


class EvidenciaTangram(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.SET_NULL, null=True, related_name="evidencias")
    equipo = models.ForeignKey(Equipos, on_delete=models.SET_NULL, null=True, related_name="evidencias")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    nombre = models.CharField(max_length=255, editable=False)

    def save(self, *args, **kwargs):
        fecha_hora = localtime().strftime('%Y-%m-%d_%H%M')  # 🔥 Usa localtime()

        if self.actividad and self.equipo:
            actividad_nombre = self.actividad.nombre.replace(" ", "").strip()[:20]
            equipo_nombre = self.equipo.nombre.replace(" ", "").strip()[:20]

            self.nombre = f"Evidencia_{actividad_nombre}_{equipo_nombre}_{fecha_hora}"
        else:
            self.nombre = f"Evidencia_SinDatos_{fecha_hora}"

        super().save(*args, **kwargs)


    def __str__(self):
        return self.nombre


class ImagenEvidencia(models.Model):
    evidencia = models.ForeignKey(EvidenciaTangram, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to='evidencias/imagenes/')
    orden = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Imagen {self.orden} de {self.evidencia.nombre}"
