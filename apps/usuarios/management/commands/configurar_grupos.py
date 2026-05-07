"""
Comando: configurar_grupos
==========================
Crea (o recrea) los 4 grupos de MonitorHub USB y les asigna los permisos
adecuados según el rol de cada perfil. También asigna los usuarios existentes
al grupo que corresponde a su campo `rol`.

Uso:
    python manage.py configurar_grupos
    python manage.py configurar_grupos --reset   # elimina y vuelve a crear
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


# ──────────────────────────────────────────────────────────────────────────────
# Mapa de permisos por grupo
# Formato: { 'app_label': ['action_model', ...] }
# Acciones: add | change | delete | view
# ──────────────────────────────────────────────────────────────────────────────

PERMISOS_ESTUDIANTE = {
    # Su propio perfil
    'usuarios': [
        'view_usuario',
        'change_usuario',
        'view_perfilestudiante',
        'change_perfilestudiante',
    ],
    # Pueden ver monitores y materias disponibles
    'monitores': [
        'view_perfilmonitor',
        'view_disponibilidadmonitor',
        'view_materia',
    ],
    # Crear y ver sus solicitudes de monitoria y tutoría
    'solicitudes': [
        'add_solicitudmonitoria',
        'view_solicitudmonitoria',
        'change_solicitudmonitoria',   # para cancelar la propia
        'add_solicitudtutoria',
        'view_solicitudtutoria',
        'change_solicitudtutoria',     # para cancelar la propia
    ],
    # Ver sesiones programadas
    'sesiones': [
        'view_sesion',
        'view_disponibilidaddocente',  # ver horarios de docentes
    ],
    # Calificar a su monitor
    'calificaciones': [
        'add_calificacion',
        'view_calificacion',
    ],
    # Mensajería con el monitor
    'mensajes': [
        'add_mensaje',
        'view_mensaje',
        'change_mensaje',
    ],
    # Recibir y marcar notificaciones
    'notificaciones': [
        'view_notificacion',
        'change_notificacion',
    ],
}

PERMISOS_MONITOR = {
    # Hereda todo lo de Estudiante (doble perfil) + gestión de su perfil monitor
    'usuarios': [
        'view_usuario',
        'change_usuario',
        'view_perfilestudiante',
        'change_perfilestudiante',
    ],
    'monitores': [
        'view_perfilmonitor',
        'change_perfilmonitor',        # editar su propia bio, etc.
        'view_materia',
        'add_disponibilidadmonitor',
        'change_disponibilidadmonitor',
        'delete_disponibilidadmonitor',
        'view_disponibilidadmonitor',
    ],
    'solicitudes': [
        # Como monitor: gestionar solicitudes recibidas
        'view_solicitudmonitoria',
        'change_solicitudmonitoria',   # aceptar / rechazar
        # Como estudiante: crear sus propias solicitudes
        'add_solicitudmonitoria',
        'add_solicitudtutoria',
        'view_solicitudtutoria',
        'change_solicitudtutoria',
    ],
    'sesiones': [
        'view_sesion',
        'add_sesion',
        'change_sesion',
        'view_disponibilidaddocente',
    ],
    'calificaciones': [
        'view_calificacion',           # ver sus propias calificaciones
        'add_calificacion',            # puede calificar como estudiante
    ],
    'mensajes': [
        'add_mensaje',
        'view_mensaje',
        'change_mensaje',
    ],
    'notificaciones': [
        'view_notificacion',
        'change_notificacion',
    ],
}

PERMISOS_DOCENTE = {
    # Perfil propio
    'usuarios': [
        'view_usuario',
        'change_usuario',
        'view_perfildocente',
        'change_perfildocente',
    ],
    # Ver monitores de sus materias (supervisión)
    'monitores': [
        'view_perfilmonitor',
        'view_materia',
        'view_disponibilidadmonitor',
    ],
    # Gestionar solicitudes de tutoría recibidas
    'solicitudes': [
        'view_solicitudmonitoria',     # supervisión de monitorias de su materia
        'view_solicitudtutoria',
        'change_solicitudtutoria',     # aceptar / rechazar
    ],
    # Publicar su disponibilidad y ver sesiones
    'sesiones': [
        'add_disponibilidaddocente',
        'change_disponibilidaddocente',
        'delete_disponibilidaddocente',
        'view_disponibilidaddocente',
        'view_sesion',
        'add_sesion',
        'change_sesion',
    ],
    # Ver calificaciones de los monitores de sus materias
    'calificaciones': [
        'view_calificacion',
    ],
    # No accede a mensajes del buzón (son entre estudiante-monitor)
    'mensajes': [
        'view_mensaje',
    ],
    'notificaciones': [
        'view_notificacion',
        'change_notificacion',
    ],
}

PERMISOS_ADMINISTRADOR = {
    # Control total sobre todos los modelos
    'usuarios': [
        'add_usuario', 'change_usuario', 'delete_usuario', 'view_usuario',
        'add_perfilestudiante', 'change_perfilestudiante', 'delete_perfilestudiante', 'view_perfilestudiante',
        'add_perfildocente', 'change_perfildocente', 'delete_perfildocente', 'view_perfildocente',
    ],
    'monitores': [
        'add_perfilmonitor', 'change_perfilmonitor', 'delete_perfilmonitor', 'view_perfilmonitor',
        'add_materia', 'change_materia', 'delete_materia', 'view_materia',
        'add_disponibilidadmonitor', 'change_disponibilidadmonitor', 'delete_disponibilidadmonitor', 'view_disponibilidadmonitor',
    ],
    'solicitudes': [
        'add_solicitudmonitoria', 'change_solicitudmonitoria', 'delete_solicitudmonitoria', 'view_solicitudmonitoria',
        'add_solicitudtutoria', 'change_solicitudtutoria', 'delete_solicitudtutoria', 'view_solicitudtutoria',
    ],
    'sesiones': [
        'add_sesion', 'change_sesion', 'delete_sesion', 'view_sesion',
        'add_disponibilidaddocente', 'change_disponibilidaddocente', 'delete_disponibilidaddocente', 'view_disponibilidaddocente',
    ],
    'calificaciones': [
        'add_calificacion', 'change_calificacion', 'delete_calificacion', 'view_calificacion',
    ],
    'mensajes': [
        'add_mensaje', 'change_mensaje', 'delete_mensaje', 'view_mensaje',
    ],
    'notificaciones': [
        'add_notificacion', 'change_notificacion', 'delete_notificacion', 'view_notificacion',
    ],
}

# ──────────────────────────────────────────────────────────────────────────────
# Definición de los 4 grupos
# ──────────────────────────────────────────────────────────────────────────────

GRUPOS = {
    'Estudiantes':     PERMISOS_ESTUDIANTE,
    'Monitores':       PERMISOS_MONITOR,
    'Docentes':        PERMISOS_DOCENTE,
    'Administradores': PERMISOS_ADMINISTRADOR,
}

# Relación entre rol del modelo Usuario y nombre del grupo
ROL_A_GRUPO = {
    'ESTUDIANTE':    'Estudiantes',
    'MONITOR':       'Monitores',
    'DOCENTE':       'Docentes',
    'ADMINISTRADOR': 'Administradores',
}


class Command(BaseCommand):
    help = 'Crea / actualiza los 4 grupos de MonitorHub con sus permisos y asigna usuarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina los grupos existentes antes de recrearlos',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('[!] Eliminando grupos existentes...'))
            Group.objects.filter(name__in=GRUPOS.keys()).delete()

        creados = 0
        actualizados = 0

        for nombre_grupo, mapa_permisos in GRUPOS.items():
            grupo, created = Group.objects.get_or_create(name=nombre_grupo)
            grupo.permissions.clear()

            permisos_asignados = 0
            permisos_faltantes = []

            for app_label, codenames in mapa_permisos.items():
                for codename in codenames:
                    try:
                        perm = Permission.objects.get(
                            codename=codename,
                            content_type__app_label=app_label,
                        )
                        grupo.permissions.add(perm)
                        permisos_asignados += 1
                    except Permission.DoesNotExist:
                        permisos_faltantes.append(f'{app_label}.{codename}')

            if created:
                creados += 1
                self.stdout.write(self.style.SUCCESS(
                    f'[+] Grupo CREADO:      {nombre_grupo:20s} - {permisos_asignados} permisos asignados'
                ))
            else:
                actualizados += 1
                self.stdout.write(self.style.SUCCESS(
                    f'[~] Grupo ACTUALIZADO: {nombre_grupo:20s} - {permisos_asignados} permisos asignados'
                ))

            if permisos_faltantes:
                self.stdout.write(self.style.WARNING(
                    f'    [!] Permisos no encontrados (modelo puede no existir aun): '
                    + ', '.join(permisos_faltantes)
                ))

        # ── Asignar usuarios existentes a su grupo correspondiente ──────────
        self.stdout.write('')
        self.stdout.write('Asignando usuarios a grupos según su rol...')

        try:
            from apps.usuarios.models import Usuario
            usuarios = Usuario.objects.all()
            asignados = 0
            sin_grupo = 0

            for usuario in usuarios:
                nombre_grupo = ROL_A_GRUPO.get(usuario.rol)
                if nombre_grupo:
                    grupo = Group.objects.get(name=nombre_grupo)
                    usuario.groups.clear()
                    usuario.groups.add(grupo)
                    asignados += 1
                else:
                    sin_grupo += 1

            self.stdout.write(self.style.SUCCESS(
                f'[OK] {asignados} usuario(s) asignados a su grupo. '
                f'{sin_grupo} sin rol reconocido.'
            ))

        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f'⚠  No se pudo asignar usuarios automáticamente: {e}'
            ))

        # ── Resumen final ────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write('-' * 60)
        self.stdout.write(self.style.SUCCESS(
            f'[OK] Configuracion completada: {creados} grupo(s) creado(s), '
            f'{actualizados} actualizado(s).'
        ))
        self.stdout.write(
            '[i] Para aplicar en Vercel/Neon ejecuta:\n'
            '    DATABASE_URL=... python manage.py configurar_grupos'
        )
