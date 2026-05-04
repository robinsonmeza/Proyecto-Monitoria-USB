from django.db import models
from apps.usuarios.models import Usuario
from apps.solicitudes.models import SolicitudMonitoria


class Mensaje(models.Model):
    remitente     = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_enviados', verbose_name='Remitente')
    destinatario  = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_recibidos', verbose_name='Destinatario')
    solicitud     = models.ForeignKey(SolicitudMonitoria, on_delete=models.CASCADE, related_name='mensajes', verbose_name='Solicitud')
    contenido     = models.TextField(verbose_name='Contenido')
    fecha_envio   = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de envío')
    fecha_lectura = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de lectura')
    es_tiempo_real = models.BooleanField(default=False, verbose_name='Enviado en tiempo real')

    class Meta:
        verbose_name        = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering            = ['fecha_envio']

    @property
    def leido(self):
        return self.fecha_lectura is not None

    def __str__(self):
        return f"{self.remitente} → {self.destinatario}: {self.contenido[:60]}..."
