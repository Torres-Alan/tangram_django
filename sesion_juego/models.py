import random
import string
from django.db import models

from equipos.models import Equipos
from estudiantes.models import Estudiante



def generar_codigo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class SesionJuego(models.Model):
    equipo = models.ForeignKey(Equipos, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=10, unique=True, default=generar_codigo)
    creada_en = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

class Message(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)  # Usuario que envía el mensaje
    contenido = models.TextField()  # Contenido del mensaje
    enviado_en = models.DateTimeField(auto_now_add=True)  # Fecha y hora en que fue enviado
    mensaje_padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)  # Mensaje al que responde

    def __str__(self):
        return f'{self.estudiante.nickname}: {self.contenido[:20]}...'  # Muestra un resumen del contenido

    class Meta:
        ordering = ['enviado_en']  # Ordenar los mensajes por la fecha
