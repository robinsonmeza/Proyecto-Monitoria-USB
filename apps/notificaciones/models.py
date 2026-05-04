from django.db import models
from apps.usuarios.models import Usuario


class Notificacion(models.Model):
    class Tipo(models.TextChoices):
        NUEVA_SOLICITUD   = 'NUEVA_SOLICITUD',   'Nueva solicitud de monitoria'
        SOLICITUD_ACEPTADA = 'SOLICITUD_ACEPTADA', 'Solicitud aceptada'
        NUEVA_SESION      = 'NUEVA_SESION',      'Nueva sesión agendada'
        SESION_CANCELADA  = 'SESION_CANCELADA',  'Sesión cancelada'
        NUEVA_CALIFICACION = 'NUEVA_CALIFICACION', 'Nueva calificación recibida'
        NUEVO_MENSAJE     = 'NUEVO_MENSAJE',     'Nuevo mensaje'
        MONITOR_APROBADO  = 'MONITOR_APROBADO',  'Perfil de monitor aprobado'
        GENERAL           = 'GENERAL',           'General'

    usuario            = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones', verbose_name='Usuario')
    tipo               = models.CharField(max_length=30, choices=Tipo.choices, default=Tipo.GENERAL, verbose_name='Tipo')
    mensaje            = models.TextField(verbose_name='Mensaje')
    fecha_envio        = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de envío')
    enviado_por_correo = models.BooleanField(default=False, verbose_name='Enviado por correo')
    leida              = models.BooleanField(default=False, verbose_name='Leída')

    class Meta:
        verbose_name        = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering            = ['-fecha_envio']

    def __str__(self):
        return f"[{self.get_tipo_display()}] → {self.usuario}: {self.mensaje[:60]}"
