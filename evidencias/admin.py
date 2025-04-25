from django.contrib import admin
from .models import EvidenciaTangram, ImagenEvidencia


class EvidenciaTangramAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'actividad', 'equipo', 'fecha_creacion')  # Columnas clave
    search_fields = (
        'nombre',
        'actividad__nombre',
        'equipo__nombre',
        'equipo__salon__grado',
        'equipo__salon__grupo',
    )
    list_filter = ('actividad', 'equipo__salon', 'fecha_creacion')  # Filtros útiles
    ordering = ('-fecha_creacion',)  # Últimas evidencias primero
    date_hierarchy = 'fecha_creacion'  # Filtro de navegación por fecha


class ImagenEvidenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'evidencia', 'orden', 'imagen')
    search_fields = ('evidencia__nombre',)
    list_filter = ('evidencia__actividad',)


admin.site.register(EvidenciaTangram, EvidenciaTangramAdmin)
admin.site.register(ImagenEvidencia, ImagenEvidenciaAdmin)
