from django.db import models
from apps.usuarios.models import Usuario, PerfilEstudiante


class Materia(models.Model):
    codigo       = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre       = models.CharField(max_length=100, verbose_name='Nombre')
    departamento = models.CharField(max_length=100, verbose_name='Departamento')

    class Meta:
        verbose_name        = 'Materia'
        verbose_name_plural = 'Materias'
        ordering            = ['nombre']

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"


class PerfilMonitor(models.Model):
    usuario           = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_monitor')
    perfil_estudiante = models.OneToOneField(PerfilEstudiante, on_delete=models.CASCADE, related_name='perfil_monitor')
    aprobado_por      = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='monitores_aprobados')
    materias          = models.ManyToManyField(Materia, related_name='monitores', blank=True, verbose_name='Materias que imparte')
    biografia         = models.TextField(blank=True, verbose_name='Biografía')
    aprobado          = models.BooleanField(default=False, verbose_name='Aprobado')
    fecha_aprobacion  = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de aprobación')
    promedio_estrellas = models.FloatField(default=0.0, verbose_name='Promedio estrellas')
    promedio_hake     = models.FloatField(default=0.0, verbose_name='Promedio Hake')
    total_sesiones    = models.PositiveIntegerField(default=0, verbose_name='Total sesiones')

    class Meta:
        verbose_name        = 'Perfil Monitor'
        verbose_name_plural = 'Perfiles Monitor'

    def __str__(self):
        return f"Monitor: {self.usuario.nombre_completo}"

    def calcular_ranking(self):
        """Score compuesto: 40% estrellas + 40% Hake + 20% volumen"""
        estrellas_norm = self.promedio_estrellas / 5.0
        hake_norm      = (self.promedio_hake + 1) / 2          # rango [-1,1] → [0,1]
        volumen_norm   = min(self.total_sesiones / 50, 1.0)    # tope suave en 50 sesiones
        return round(
            (0.40 * estrellas_norm) + (0.40 * hake_norm) + (0.20 * volumen_norm),
            4
        )


class DisponibilidadMonitor(models.Model):
    class DiaSemana(models.TextChoices):
        LUNES    = 'LUNES',    'Lunes'
        MARTES   = 'MARTES',   'Martes'
        MIERCOLES = 'MIERCOLES', 'Miércoles'
        JUEVES   = 'JUEVES',   'Jueves'
        VIERNES  = 'VIERNES',  'Viernes'
        SABADO   = 'SABADO',   'Sábado'
        DOMINGO  = 'DOMINGO',  'Domingo'

    class Modalidad(models.TextChoices):
        PRESENCIAL = 'PRESENCIAL', 'Presencial'
        VIRTUAL    = 'VIRTUAL',    'Virtual'

    monitor     = models.ForeignKey(PerfilMonitor, on_delete=models.CASCADE, related_name='disponibilidades')
    dia_semana  = models.CharField(max_length=10, choices=DiaSemana.choices, verbose_name='Día')
    hora_inicio = models.TimeField(verbose_name='Hora de inicio')
    hora_fin    = models.TimeField(verbose_name='Hora de fin')
    modalidad   = models.CharField(max_length=10, choices=Modalidad.choices, verbose_name='Modalidad')
    ubicacion   = models.CharField(max_length=200, blank=True, verbose_name='Ubicación')
    activo      = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name        = 'Disponibilidad'
        verbose_name_plural = 'Disponibilidades'
        ordering            = ['dia_semana', 'hora_inicio']

    def __str__(self):
        return f"{self.monitor} — {self.get_dia_semana_display()} {self.hora_inicio}–{self.hora_fin} ({self.get_modalidad_display()})"
