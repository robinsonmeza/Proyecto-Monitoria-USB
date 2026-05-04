from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .models import Calificacion
from apps.solicitudes.models import SolicitudMonitoria


class CalificarView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, solicitud_pk):
        solicitud = get_object_or_404(
            SolicitudMonitoria, pk=solicitud_pk, estado='COMPLETADO'
        )
        # Check if already rated
        if hasattr(solicitud, 'calificacion'):
            messages.info(request, 'Esta monitoria ya fue calificada.')
            return redirect('solicitudes:lista')

        return render(request, 'calificaciones/calificar.html', {
            'solicitud':   solicitud,
            'monitor':     solicitud.monitor,
            'notif_count': request.user.notificaciones.filter(leida=False).count(),
        })

    def post(self, request, solicitud_pk):
        solicitud = get_object_or_404(
            SolicitudMonitoria, pk=solicitud_pk, estado='COMPLETADO'
        )

        # Must be the student of this solicitud
        try:
            perfil_estudiante = request.user.perfil_estudiante
        except Exception:
            messages.error(request, 'Solo los estudiantes pueden calificar monitorias.')
            return redirect('usuarios:dashboard')

        if solicitud.estudiante != perfil_estudiante:
            messages.error(request, 'No tienes permiso para calificar esta monitoria.')
            return redirect('solicitudes:lista')

        # Prevent duplicate
        if hasattr(solicitud, 'calificacion'):
            messages.info(request, 'Esta monitoria ya fue calificada.')
            return redirect('solicitudes:lista')

        estrellas   = int(request.POST.get('estrellas', 3))
        comentario  = request.POST.get('comentario_privado', '').strip()
        nota_final  = float(request.POST.get('nota_final', 0))

        # Clamp values
        estrellas  = max(1, min(5, estrellas))
        nota_final = max(0.0, min(5.0, nota_final))

        Calificacion.objects.create(
            solicitud=solicitud,
            estudiante=perfil_estudiante,
            monitor=solicitud.monitor,
            estrellas=estrellas,
            comentario_privado=comentario,
            nota_final=nota_final,
        )

        messages.success(
            request,
            '¡Calificación guardada! Gracias por tu retroalimentación.'
        )
        return redirect('solicitudes:lista')


class MisCalificacionesView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        user = request.user

        if user.rol == 'MONITOR':
            try:
                calificaciones = (
                    Calificacion.objects
                    .filter(monitor=user.perfil_monitor)
                    .select_related(
                        'estudiante__usuario',
                        'solicitud__materia',
                    )
                    .order_by('-fecha_creacion')
                )
            except Exception:
                calificaciones = Calificacion.objects.none()
        else:
            try:
                calificaciones = (
                    Calificacion.objects
                    .filter(estudiante=user.perfil_estudiante)
                    .select_related(
                        'monitor__usuario',
                        'solicitud__materia',
                    )
                    .order_by('-fecha_creacion')
                )
            except Exception:
                calificaciones = Calificacion.objects.none()

        return render(request, 'calificaciones/mis_calificaciones.html', {
            'calificaciones': calificaciones,
            'notif_count':    user.notificaciones.filter(leida=False).count(),
        })
