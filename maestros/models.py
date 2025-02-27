# maestros/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Maestro(AbstractUser):
    #Los campos es username, email, password

    # Los campos como nombre, correo, etc., ya están en el modelo AbstractUser,
    # pero puedes agregar cualquier otro campo adicional que necesites.
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username  # Utiliza el nombre de usuario por defecto

    class Meta:
        verbose_name = "Maestro"
        verbose_name_plural = "Maestros"
