from django.contrib import admin
from equipos.models import Equipos

class EquiposAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'created_by', 'salon', 'created_at')  # Mostrar los campos relevantes
    search_fields = ('nombre', 'created_by__username', 'salon__grado', 'salon__grupo')  # Puedes buscar por nombre de equipo, nombre del maestro o información del salón
    list_filter = ('salon', 'created_by')  # Filtrar por salón o por maestro
    ordering = ('nombre',)  # Ordenar por nombre del equipo

# Registrar el modelo Equipos en el admin con las configuraciones personalizadas
admin.site.register(Equipos, EquiposAdmin)
