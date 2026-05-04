from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PerfilEstudiante, PerfilDocente


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    ordering        = ('email',)
    list_display    = ('email', 'first_name', 'last_name', 'rol', 'activo', 'fecha_creacion')
    list_filter     = ('rol', 'activo')
    search_fields   = ('email', 'first_name', 'last_name')
    fieldsets = (
        (None,              {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'id_microsoft')}),
        ('Rol y permisos',  {'fields': ('rol', 'activo', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas',          {'fields': ('last_login', 'fecha_creacion')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'first_name', 'last_name', 'rol', 'password1', 'password2')}),
    )
    readonly_fields = ('fecha_creacion', 'last_login')


@admin.register(PerfilEstudiante)
class PerfilEstudianteAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'codigo_estudiante', 'programa', 'semestre')
    search_fields = ('usuario__email', 'usuario__first_name', 'codigo_estudiante', 'programa')
    list_filter   = ('programa', 'semestre')


@admin.register(PerfilDocente)
class PerfilDocenteAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'departamento')
    search_fields = ('usuario__email', 'usuario__first_name', 'departamento')
    list_filter   = ('departamento',)
    filter_horizontal = ('materias',)
