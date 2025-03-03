# salones/admin.py
from django.contrib import admin
from .models import Salon

# Registrar el modelo Salon en el admin
admin.site.register(Salon)
