from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.solicitudes.models import SolicitudMonitoria
from apps.usuarios.models import PerfilEstudiante
from apps.monitores.models import PerfilMonitor


class Calificacion(models.Model):
    solicitud          = models.OneToOneField(SolicitudMonitoria, on_delete=models.CASCADE, related_name='calificacion', verbose_name='Solicitud')
    estudiante         = models.ForeignKey(PerfilEstudiante, on_delete=models.CASCADE, related_name='calificaciones_dadas', verbose_name='Estudiante')
    monitor            = models.ForeignKey(PerfilMonitor, on_delete=models.CASCADE, related_name='calificaciones_recibidas', verbose_name='Monitor')
    estrellas          = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='Estrellas (1-5)')
    comentario_privado = models.TextField(blank=True, verbose_name='Comentario privado (solo docente)')
    nota_final         = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], verbose_name='Nota final')
    puntaje_hake       = models.FloatField(default=0.0, verbose_name='Puntaje Hake')
    fecha_creacion     = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de calificación')

    class Meta:
        verbose_name        = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        ordering            = ['-fecha_creacion']

    def calcular_hake(self):
        """
        Ganancia Normalizada de Hake:
        g = (nota_final - nota_inicial) / (nota_maxima - nota_inicial)
        - g >= 0.7 : ganancia alta
        - 0.3 <= g < 0.7 : ganancia media
        - g < 0.3 : ganancia baja
        - g < 0   : retroceso (penaliza al monitor)
        """
        nota_inicial = self.solicitud.nota_inicial
        nota_maxima  = 5.0
        denominador  = nota_maxima - nota_inicial
        if denominador == 0:
            return 1.0  # ya estaba en el tope, no hay mejora posible
        g = (self.nota_final - nota_inicial) / denominador
        return round(g, 4)

    @property
    def nivel_hake(self):
        if self.puntaje_hake >= 0.7:
            return 'Alta'
        elif self.puntaje_hake >= 0.3:
            return 'Media'
        elif self.puntaje_hake >= 0:
            return 'Baja'
        return 'Retroceso'

    def save(self, *args, **kwargs):
        self.puntaje_hake = self.calcular_hake()
        super().save(*args, **kwargs)
        self._actualizar_promedios_monitor()

    def _actualizar_promedios_monitor(self):
        """Recalcula promedio_estrellas, promedio_hake y total_sesiones del monitor."""
        from django.db.models import Avg, Count
        stats = Calificacion.objects.filter(monitor=self.monitor).aggregate(
            avg_estrellas = Avg('estrellas'),
            avg_hake      = Avg('puntaje_hake'),
            total         = Count('id')
        )
        self.monitor.promedio_estrellas = round(stats['avg_estrellas'] or 0.0, 2)
        self.monitor.promedio_hake      = round(stats['avg_hake'] or 0.0, 4)
        self.monitor.total_sesiones     = stats['total'] or 0
        self.monitor.save(update_fields=['promedio_estrellas', 'promedio_hake', 'total_sesiones'])

    def __str__(self):
        return f"{self.estrellas}⭐ | Hake: {self.puntaje_hake} ({self.nivel_hake}) — {self.estudiante} → {self.monitor}"
