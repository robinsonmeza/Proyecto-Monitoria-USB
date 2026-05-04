from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View

from .models import SolicitudMonitoria, SolicitudTutoria
from apps.monitores.models import PerfilMonitor, Materia
from apps.usuarios.models import PerfilDocente
from apps.notificaciones.models import Notificacion


# ── Monitorías (flujo monitor ← supervisor docente) ─────────────────────────

class NuevaSolicitudView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, monitor_pk):
        monitor = get_object_or_404(PerfilMonitor, pk=monitor_pk, aprobado=True)
        return render(request, 'monitores/detalle.html', {
            'monitor':          monitor,
            'materias_monitor': monitor.materias.all(),
            'disponibilidades': monitor.disponibilidades.filter(activo=True),
            'docentes':         PerfilDocente.objects.all().select_related('usuario'),
            'notif_count':      request.user.notificaciones.filter(leida=False).count(),
        })

    def post(self, request, monitor_pk):
        monitor = get_object_or_404(PerfilMonitor, pk=monitor_pk, aprobado=True)

        try:
            perfil_estudiante = request.user.perfil_estudiante
        except Exception:
            messages.error(request, 'Solo los estudiantes pueden solicitar monitorias.')
            return redirect('usuarios:dashboard')

        materia    = get_object_or_404(Materia, pk=request.POST.get('materia'))
        docente    = get_object_or_404(PerfilDocente, pk=request.POST.get('docente'))
        nota_ini   = float(request.POST.get('nota_inicial', 0))
        nota_corte = float(request.POST.get('nota_corte_actual', 0))
        notas      = request.POST.get('notas', '')

        solicitud = SolicitudMonitoria.objects.create(
            estudiante=perfil_estudiante,
            monitor=monitor,
            materia=materia,
            docente=docente,
            nota_inicial=nota_ini,
            nota_corte_actual=nota_corte,
            notas=notas,
            estado='ACTIVO',
        )

        Notificacion.objects.create(
            usuario=request.user,
            tipo='SOLICITUD_ACEPTADA',
            mensaje=(
                f'Tu solicitud de monitoria con {monitor.usuario.nombre_completo} '
                f'en {materia.nombre} fue registrada exitosamente.'
            ),
        )
        Notificacion.objects.create(
            usuario=monitor.usuario,
            tipo='NUEVA_SOLICITUD',
            mensaje=f'{request.user.nombre_completo} quiere monitoria en {materia.nombre}.',
        )
        Notificacion.objects.create(
            usuario=docente.usuario,
            tipo='NUEVA_SOLICITUD',
            mensaje=(
                f'{request.user.nombre_completo} está tomando monitoria en '
                f'{materia.nombre} con {monitor.usuario.nombre_completo}.'
            ),
        )

        messages.success(
            request,
            f'Solicitud enviada. Se notificó a {monitor.usuario.nombre_completo} '
            f'y al docente {docente.usuario.nombre_completo}.'
        )
        return redirect('solicitudes:lista')


class MisSolicitudesView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        user = request.user

        if user.rol == 'ESTUDIANTE':
            try:
                solicitudes = (
                    SolicitudMonitoria.objects
                    .filter(estudiante=user.perfil_estudiante)
                    .select_related('monitor__usuario', 'materia', 'docente__usuario')
                    .prefetch_related('calificacion')
                    .order_by('-fecha_creacion')
                )
                tutorias = (
                    SolicitudTutoria.objects
                    .filter(estudiante=user.perfil_estudiante)
                    .select_related('docente__usuario', 'materia')
                    .order_by('-fecha_creacion')
                )
            except Exception:
                solicitudes = SolicitudMonitoria.objects.none()
                tutorias    = SolicitudTutoria.objects.none()

        elif user.rol == 'MONITOR':
            try:
                solicitudes = (
                    SolicitudMonitoria.objects
                    .filter(monitor=user.perfil_monitor)
                    .select_related('estudiante__usuario', 'materia', 'docente__usuario')
                    .order_by('-fecha_creacion')
                )
            except Exception:
                solicitudes = SolicitudMonitoria.objects.none()
            tutorias = SolicitudTutoria.objects.none()

        elif user.rol == 'DOCENTE':
            try:
                solicitudes = (
                    SolicitudMonitoria.objects
                    .filter(docente=user.perfil_docente)
                    .select_related('monitor__usuario', 'estudiante__usuario', 'materia')
                    .order_by('-fecha_creacion')
                )
                tutorias = (
                    SolicitudTutoria.objects
                    .filter(docente=user.perfil_docente)
                    .select_related('estudiante__usuario', 'materia')
                    .order_by('-fecha_creacion')
                )
            except Exception:
                solicitudes = SolicitudMonitoria.objects.none()
                tutorias    = SolicitudTutoria.objects.none()

        else:
            solicitudes = (
                SolicitudMonitoria.objects
                .all()
                .select_related('monitor__usuario', 'estudiante__usuario', 'materia')
                .order_by('-fecha_creacion')
            )
            tutorias = (
                SolicitudTutoria.objects
                .all()
                .select_related('docente__usuario', 'estudiante__usuario', 'materia')
                .order_by('-fecha_creacion')
            )

        return render(request, 'solicitudes/mis_solicitudes.html', {
            'solicitudes': solicitudes,
            'tutorias':    tutorias,
            'notif_count': user.notificaciones.filter(leida=False).count(),
        })


# ── Tutorías (flujo directo estudiante → docente) ────────────────────────────

class NuevaTutoriaView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, docente_pk):
        docente = get_object_or_404(PerfilDocente, pk=docente_pk)
        from apps.sesiones.models import DisponibilidadDocente
        return render(request, 'solicitudes/nueva_tutoria.html', {
            'docente':          docente,
            'disponibilidades': DisponibilidadDocente.objects.filter(
                docente=docente, activo=True
            ).select_related('materia'),
            'materias':         docente.materias.all(),
            'notif_count':      request.user.notificaciones.filter(leida=False).count(),
        })

    def post(self, request, docente_pk):
        docente = get_object_or_404(PerfilDocente, pk=docente_pk)

        try:
            perfil_estudiante = request.user.perfil_estudiante
        except Exception:
            messages.error(request, 'Solo los estudiantes pueden solicitar tutorías.')
            return redirect('usuarios:dashboard')

        materia    = get_object_or_404(Materia, pk=request.POST.get('materia'))
        nota_ini   = float(request.POST.get('nota_inicial', 0))
        nota_corte = float(request.POST.get('nota_corte_actual', 0))
        notas      = request.POST.get('notas', '').strip()

        SolicitudTutoria.objects.create(
            estudiante=perfil_estudiante,
            docente=docente,
            materia=materia,
            nota_inicial=nota_ini,
            nota_corte_actual=nota_corte,
            notas=notas,
        )

        # Notificar al docente
        Notificacion.objects.create(
            usuario=docente.usuario,
            tipo='NUEVA_SOLICITUD',
            mensaje=(
                f'{request.user.nombre_completo} solicita tutoría en '
                f'{materia.nombre}.'
            ),
        )
        # Confirmar al estudiante
        Notificacion.objects.create(
            usuario=request.user,
            tipo='SOLICITUD_ACEPTADA',
            mensaje=(
                f'Tu solicitud de tutoría con el docente '
                f'{docente.usuario.nombre_completo} en {materia.nombre} '
                f'fue registrada.'
            ),
        )

        messages.success(
            request,
            f'Solicitud de tutoría enviada al docente {docente.usuario.nombre_completo}.'
        )
        return redirect('solicitudes:lista')
