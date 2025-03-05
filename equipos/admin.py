from django.contrib import admin

from equipos.models import Equipos
class EquiposAdmin(admin.ModelAdmin):
    list_display = ('id',)  # Agregar el campo 'salon'


# Register your models here.
admin.site.register(Equipos, EquiposAdmin)
