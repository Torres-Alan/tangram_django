# maestros/admin.py
from django.contrib import admin
from .models import Maestro

class MaestroAdmin(admin.ModelAdmin):
    list_display = ('id','username', 'email', 'fecha_creacion', 'is_staff', 'is_active')
    search_fields = ('username', 'email')  # Puedes buscar por nombre o correo
    list_filter = ('is_active', 'is_staff')  # Puedes filtrar por estado o si es staff

# Registrando el modelo en el admin
admin.site.register(Maestro, MaestroAdmin)
