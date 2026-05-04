from django.contrib import admin
from .models import Mensaje


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display  = ('remitente', 'destinatario', 'solicitud', 'fecha_envio', 'leido', 'es_tiempo_real')
    list_filter   = ('es_tiempo_real', 'fecha_envio')
    search_fields = ('remitente__email', 'destinatario__email', 'contenido')
    readonly_fields = ('fecha_envio',)

    @admin.display(description='Leído', boolean=True)
    def leido(self, obj):
        return obj.leido
