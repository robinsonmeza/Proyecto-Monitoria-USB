from django.contrib import admin
from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'tipo', 'mensaje_corto', 'fecha_envio', 'leida', 'enviado_por_correo')
    list_filter   = ('tipo', 'leida', 'enviado_por_correo', 'fecha_envio')
    search_fields = ('usuario__email', 'mensaje')
    readonly_fields = ('fecha_envio',)

    @admin.display(description='Mensaje')
    def mensaje_corto(self, obj):
        return obj.mensaje[:80]
