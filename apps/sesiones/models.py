from django.db import models
from apps.solicitudes.models import SolicitudMonitoria


class Sesion(models.Model):
    class Estado(models.TextChoices):
        PROGRAMADA = 'PROGRAMADA', 'Programada'
        COMPLETADA = 'COMPLETADA', 'Completada'
        CANCELADA  = 'CANCELADA',  'Cancelada'

    class Modalidad(models.TextChoices):
        PRESENCIAL = 'PRESENCIAL', 'Presencial'
        VIRTUAL    = 'VIRTUAL',    'Virtual'

    solicitud        = models.ForeignKey(SolicitudMonitoria, on_delete=models.CASCADE, related_name='sesiones', verbose_name='Solicitud')
    fecha_hora       = models.DateTimeField(verbose_name='Fecha y hora')
    duracion_minutos = models.PositiveIntegerField(default=60, verbose_name='Duración (minutos)')
    modalidad        = models.CharField(max_length=10, choices=Modalidad.choices, verbose_name='Modalidad')
    url_teams        = models.URLField(blank=True, verbose_name='URL Teams')
    ubicacion        = models.CharField(max_length=200, blank=True, verbose_name='Ubicación')
    estado           = models.CharField(max_length=15, choices=Estado.choices, default=Estado.PROGRAMADA, verbose_name='Estado')

    class Meta:
        verbose_name        = 'Sesión'
        verbose_name_plural = 'Sesiones'
        ordering            = ['-fecha_hora']

    def __str__(self):
        return f"Sesión [{self.get_estado_display()}] — {self.solicitud} — {self.fecha_hora:%d/%m/%Y %H:%M}"


# ── Disponibilidad de Docente para Tutorías ─────────────────────────────────

class DisponibilidadDocente(models.Model):
    class DiaSemana(models.TextChoices):
        LUNES     = 'LUNES',     'Lunes'
        MARTES    = 'MARTES',    'Martes'
        MIERCOLES = 'MIERCOLES', 'Miércoles'
        JUEVES    = 'JUEVES',    'Jueves'
        VIERNES   = 'VIERNES',   'Viernes'
        SABADO    = 'SABADO',    'Sábado'

    class Modalidad(models.TextChoices):
        PRESENCIAL = 'PRESENCIAL', 'Presencial'
        VIRTUAL    = 'VIRTUAL',    'Virtual'
        AMBAS      = 'AMBAS',      'Presencial y Virtual'

    docente     = models.ForeignKey(
        'usuarios.PerfilDocente',
        on_delete=models.CASCADE,
        related_name='disponibilidades',
        verbose_name='Docente',
    )
    materia     = models.ForeignKey(
        'monitores.Materia',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='disponibilidades_docente',
        verbose_name='Materia (opcional)',
    )
    dia_semana  = models.CharField(max_length=10, choices=DiaSemana.choices, verbose_name='Día')
    hora_inicio = models.TimeField(verbose_name='Hora de inicio')
    hora_fin    = models.TimeField(verbose_name='Hora de fin')
    modalidad   = models.CharField(max_length=10, choices=Modalidad.choices, verbose_name='Modalidad')
    ubicacion   = models.CharField(max_length=200, blank=True, verbose_name='Ubicación / Enlace')
    activo      = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name        = 'Disponibilidad Docente'
        verbose_name_plural = 'Disponibilidades Docente'
        ordering            = ['dia_semana', 'hora_inicio']

    def __str__(self):
        materia_str = f" [{self.materia.nombre}]" if self.materia else ""
        return (
            f"{self.docente.usuario.nombre_completo}{materia_str} — "
            f"{self.get_dia_semana_display()} {self.hora_inicio}–{self.hora_fin}"
        )
