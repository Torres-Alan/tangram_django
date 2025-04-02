from django.contrib import admin
from .models import SesionJuego

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

admin.site.register(SesionJuego, SesionJuegoAdmin)
