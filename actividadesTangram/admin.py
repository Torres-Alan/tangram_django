from django.contrib import admin
from .models import Actividad

class ActividadAdmin(admin.ModelAdmin):
    # Agregamos 'maestroId' para que se vea en el panel de administración
    list_display = ('id', 'nombre', 'horas', 'minutos', 'segundos', 'salon', 'banco_tangrams', 'maestroId', 'activo')  # Ahora incluye 'maestroId'
    search_fields = ('nombre',)
    list_filter = ('salon', 'maestroId', 'activo')  # También puedes filtrar por 'maestroId' si quieres
    ordering = ('nombre',)
    fieldsets = (
        (None, {
            'fields': ('nombre', 'horas', 'minutos', 'segundos', 'salon', 'maestroId', 'activo')  # Agregado 'maestroId'
        }),
        ('Banco de Tangrams', {
            'fields': ('banco_tangrams',)
        }),
    )

admin.site.register(Actividad, ActividadAdmin)
