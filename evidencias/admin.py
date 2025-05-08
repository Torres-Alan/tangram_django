from django.contrib import admin
from .models import EvidenciaTangram, ImagenEvidencia, EstadisticaEvidencia


class EvidenciaTangramAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'actividad', 'equipo', 'fecha_creacion')
    search_fields = (
        'nombre',
        'actividad__nombre',
        'equipo__nombre',
        'equipo__salon__grado',
        'equipo__salon__grupo',
    )
    list_filter = ('actividad', 'equipo__salon', 'fecha_creacion')
    ordering = ('-fecha_creacion',)
    date_hierarchy = 'fecha_creacion'


class ImagenEvidenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'evidencia', 'orden', 'imagen')
    search_fields = ('evidencia__nombre',)
    list_filter = ('evidencia__actividad',)


class EstadisticaEvidenciaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'evidencia',
        'nickname_estudiante',
        'nombre_estudiante',
        'mensajes_enviados',
        'respuestas_enviadas',
        'piezas_movidas'
    )
    search_fields = ('nickname_estudiante', 'nombre_estudiante', 'evidencia__nombre')
    list_filter = ('evidencia__actividad', 'evidencia__equipo')
    ordering = ('-evidencia__fecha_creacion',)


admin.site.register(EvidenciaTangram, EvidenciaTangramAdmin)
admin.site.register(ImagenEvidencia, ImagenEvidenciaAdmin)
admin.site.register(EstadisticaEvidencia, EstadisticaEvidenciaAdmin)