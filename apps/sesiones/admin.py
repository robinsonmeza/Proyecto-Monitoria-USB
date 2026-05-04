from django.contrib import admin
from .models import Sesion


@admin.register(Sesion)
class SesionAdmin(admin.ModelAdmin):
    list_display  = ('solicitud', 'fecha_hora', 'duracion_minutos', 'modalidad', 'estado')
    list_filter   = ('estado', 'modalidad', 'fecha_hora')
    search_fields = ('solicitud__estudiante__usuario__email', 'solicitud__monitor__usuario__email')
    readonly_fields = ('fecha_hora',)
