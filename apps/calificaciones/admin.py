from django.contrib import admin
from .models import Calificacion


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display    = ('estudiante', 'monitor', 'estrellas', 'nota_final', 'puntaje_hake', 'nivel_hake', 'fecha_creacion')
    list_filter     = ('estrellas', 'fecha_creacion')
    search_fields   = ('estudiante__usuario__email', 'monitor__usuario__email')
    readonly_fields = ('puntaje_hake', 'nivel_hake', 'fecha_creacion')

    @admin.display(description='Nivel Hake')
    def nivel_hake(self, obj):
        return obj.nivel_hake
