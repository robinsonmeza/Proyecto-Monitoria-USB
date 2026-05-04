from django.contrib import admin
from .models import SolicitudMonitoria


@admin.register(SolicitudMonitoria)
class SolicitudMonitoriaAdmin(admin.ModelAdmin):
    list_display  = ('estudiante', 'monitor', 'materia', 'docente', 'estado', 'nota_inicial', 'nota_corte_actual', 'fecha_creacion')
    list_filter   = ('estado', 'materia', 'fecha_creacion')
    search_fields = ('estudiante__usuario__email', 'monitor__usuario__email', 'materia__nombre')
    readonly_fields = ('fecha_creacion',)
    ordering      = ('-fecha_creacion',)
