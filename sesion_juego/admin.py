from django.contrib import admin
from .models import SesionJuego, Message
class SesionJuegoAdmin(admin.ModelAdmin):
    list_display = ('id', 'equipo', 'codigo', 'creada_en', 'activa')
    search_fields = ('codigo', 'equipo__nombre')
    list_filter = ('activa', 'equipo')
    ordering = ('creada_en',)

    readonly_fields = ('creada_en',)

    fieldsets = (
        (None, {
            'fields': ('equipo', 'codigo', 'activa')
        }),
        ('Fecha y Estado', {
            'fields': ('creada_en',),
            'classes': ('collapse',),
        }),
    )
    
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudiante', 'contenido', 'enviado_en', 'mensaje_padre')  # Mostrar estos campos en la lista
    search_fields = ('estudiantenickname', 'contenido')  # Buscar por el nickname del estudiante o contenido del mensaje
    list_filter = ('estudiante', 'mensaje_padre')  # Filtrar por estudiante o mensaje padre
    ordering = ('enviado_en',)  # Ordenar por la fecha de envío

    readonly_fields = ('enviado_en',)  # Hacer que 'enviado_en' sea solo de lectura

    fieldsets = (
        (None, {
            'fields': ('estudiante', 'contenido', 'mensaje_padre')  # Campos principales
        }),
        ('Detalles', {
            'fields': ('enviado_en',),  # Detalles del mensaje
            'classes': ('collapse',),
        }),
    )


admin.site.register(SesionJuego, SesionJuegoAdmin)
admin.site.register(Message,MessageAdmin)
