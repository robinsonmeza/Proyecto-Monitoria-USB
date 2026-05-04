from django.contrib import admin
from .models import Materia, PerfilMonitor, DisponibilidadMonitor


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display  = ('codigo', 'nombre', 'departamento')
    search_fields = ('codigo', 'nombre', 'departamento')
    list_filter   = ('departamento',)


class DisponibilidadInline(admin.TabularInline):
    model  = DisponibilidadMonitor
    extra  = 1
    fields = ('dia_semana', 'hora_inicio', 'hora_fin', 'modalidad', 'ubicacion', 'activo')


@admin.register(PerfilMonitor)
class PerfilMonitorAdmin(admin.ModelAdmin):
    list_display      = ('usuario', 'aprobado', 'promedio_estrellas', 'promedio_hake', 'total_sesiones', 'ranking')
    list_filter       = ('aprobado',)
    search_fields     = ('usuario__email', 'usuario__first_name', 'usuario__last_name')
    filter_horizontal = ('materias',)
    readonly_fields   = ('promedio_estrellas', 'promedio_hake', 'total_sesiones', 'ranking')
    inlines           = [DisponibilidadInline]

    @admin.display(description='Ranking')
    def ranking(self, obj):
        return round(obj.calcular_ranking(), 3)


@admin.register(DisponibilidadMonitor)
class DisponibilidadMonitorAdmin(admin.ModelAdmin):
    list_display = ('monitor', 'dia_semana', 'hora_inicio', 'hora_fin', 'modalidad', 'activo')
    list_filter  = ('dia_semana', 'modalidad', 'activo')
