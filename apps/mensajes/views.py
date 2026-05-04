from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.utils import timezone
from .models import Mensaje
from apps.solicitudes.models import SolicitudMonitoria
from apps.notificaciones.models import Notificacion


class BandejaView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        user = request.user

        # Collect solicitudes where the user is a participant
        if hasattr(user, 'perfil_estudiante'):
            solicitudes = (
                SolicitudMonitoria.objects
                .filter(estudiante=user.perfil_estudiante)
                .select_related('monitor__usuario', 'materia', 'estudiante__usuario')
                .order_by('-fecha_creacion')
            )
        elif hasattr(user, 'perfil_monitor'):
            solicitudes = (
                SolicitudMonitoria.objects
                .filter(monitor=user.perfil_monitor)
                .select_related('estudiante__usuario', 'materia', 'monitor__usuario')
                .order_by('-fecha_creacion')
            )
        else:
            solicitudes = SolicitudMonitoria.objects.none()

        solicitud_activa_pk = request.GET.get('solicitud')
        solicitud_activa    = None
        mensajes_activos    = []

        if solicitud_activa_pk:
            solicitud_activa = get_object_or_404(
                SolicitudMonitoria, pk=solicitud_activa_pk
            )
            mensajes_activos = (
                Mensaje.objects
                .filter(solicitud=solicitud_activa)
                .select_related('remitente')
            )
            # Mark incoming messages as read
            Mensaje.objects.filter(
                solicitud=solicitud_activa,
                destinatario=user,
                fecha_lectura__isnull=True,
            ).update(fecha_lectura=timezone.now())

        return render(request, 'mensajes/bandeja.html', {
            'solicitudes':     solicitudes,
            'solicitud_activa': solicitud_activa,
            'mensajes':        mensajes_activos,
            'notif_count':     user.notificaciones.filter(leida=False).count(),
        })


class EnviarMensajeView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, solicitud_pk):
        solicitud = get_object_or_404(SolicitudMonitoria, pk=solicitud_pk)
        contenido = request.POST.get('contenido', '').strip()

        if not contenido:
            return redirect(f'/mensajes/?solicitud={solicitud_pk}')

        user = request.user

        # Determine the recipient (the other party)
        if hasattr(user, 'perfil_estudiante') and solicitud.estudiante == user.perfil_estudiante:
            destinatario = solicitud.monitor.usuario
        elif hasattr(user, 'perfil_monitor') and solicitud.monitor == user.perfil_monitor:
            destinatario = solicitud.estudiante.usuario
        else:
            # Fallback: send to the monitor
            destinatario = solicitud.monitor.usuario

        Mensaje.objects.create(
            remitente=user,
            destinatario=destinatario,
            solicitud=solicitud,
            contenido=contenido,
            es_tiempo_real=False,
        )

        Notificacion.objects.create(
            usuario=destinatario,
            tipo='NUEVO_MENSAJE',
            mensaje=f'Nuevo mensaje de {user.nombre_completo} sobre {solicitud.materia.nombre}.',
        )

        return redirect(f'/mensajes/?solicitud={solicitud_pk}')
