from django.db import models
from apps.usuarios.models import PerfilEstudiante, PerfilDocente
from apps.monitores.models import PerfilMonitor, Materia


class SolicitudMonitoria(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE  = 'PENDIENTE',  'Pendiente'
        ACTIVO     = 'ACTIVO',     'Activo'
        COMPLETADO = 'COMPLETADO', 'Completado'
        CANCELADO  = 'CANCELADO',  'Cancelado'

    estudiante        = models.ForeignKey(PerfilEstudiante, on_delete=models.CASCADE, related_name='solicitudes', verbose_name='Estudiante')
    monitor           = models.ForeignKey(PerfilMonitor, on_delete=models.CASCADE, related_name='solicitudes', verbose_name='Monitor')
    materia           = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='solicitudes', verbose_name='Materia')
    docente           = models.ForeignKey(PerfilDocente, on_delete=models.CASCADE, related_name='solicitudes', verbose_name='Docente')
    nota_inicial      = models.FloatField(verbose_name='Nota inicial')
    nota_corte_actual = models.FloatField(verbose_name='Nota del corte actual')
    estado            = models.CharField(max_length=15, choices=Estado.choices, default=Estado.PENDIENTE, verbose_name='Estado')
    fecha_creacion    = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    notas             = models.TextField(blank=True, verbose_name='Notas adicionales')

    class Meta:
        verbose_name        = 'Solicitud de Monitoria'
        verbose_name_plural = 'Solicitudes de Monitoria'
        ordering            = ['-fecha_creacion']

    def __str__(self):
        return f"{self.estudiante} → {self.monitor} | {self.materia} [{self.get_estado_display()}]"


# ── Solicitud de Tutoría (estudiante → docente, flujo directo) ───────────────

class SolicitudTutoria(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE  = 'PENDIENTE',  'Pendiente'
        ACTIVO     = 'ACTIVO',     'Activo'
        COMPLETADO = 'COMPLETADO', 'Completado'
        CANCELADO  = 'CANCELADO',  'Cancelado'

    estudiante        = models.ForeignKey(
        PerfilEstudiante,
        on_delete=models.CASCADE,
        related_name='solicitudes_tutoria',
        verbose_name='Estudiante',
    )
    docente           = models.ForeignKey(
        PerfilDocente,
        on_delete=models.CASCADE,
        related_name='solicitudes_tutoria',
        verbose_name='Docente',
    )
    materia           = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE,
        related_name='solicitudes_tutoria',
        verbose_name='Materia',
    )
    nota_inicial      = models.FloatField(verbose_name='Nota inicial')
    nota_corte_actual = models.FloatField(verbose_name='Nota del corte actual')
    estado            = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='Estado',
    )
    fecha_creacion    = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de solicitud')
    notas             = models.TextField(blank=True, verbose_name='Notas adicionales')

    class Meta:
        verbose_name        = 'Solicitud de Tutoría'
        verbose_name_plural = 'Solicitudes de Tutoría'
        ordering            = ['-fecha_creacion']

    def __str__(self):
        return (
            f"{self.estudiante} → Tutoría con {self.docente} | "
            f"{self.materia} [{self.get_estado_display()}]"
        )
