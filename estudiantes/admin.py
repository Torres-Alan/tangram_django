# estudiantes/admin.py
from django.contrib import admin
from .models import Estudiante

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellidos', 'nickname')  # Mostrar solo los campos relevantes
    search_fields = ('nombre', 'apellidos', 'nickname')  # Hacer los campos buscables
    list_filter = ('nickname',)  # Filtrar por nickname
    ordering = ('nombre',)  # Ordenar por nombre de manera predeterminada
