# salones/admin.py
from django.contrib import admin
from .models import Salon

class SalonAdmin(admin.ModelAdmin):
    list_display = ('id', 'grado', 'grupo', 'ciclo_escolar_inicio', 'ciclo_escolar_fin', 'docente')  # Incluir el id
    search_fields = ('grado', 'grupo')  # Puedes buscar por grado o grupo
    list_filter = ('grado', 'grupo', 'docente')  # Puedes filtrar por grado, grupo o docente
    ordering = ('grado', 'grupo')  # Ordenar por grado y grupo de manera predeterminada

# Registrar el modelo Salon en el admin con las configuraciones personalizadas
admin.site.register(Salon, SalonAdmin)
