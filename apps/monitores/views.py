from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .models import PerfilMonitor, Materia


class ListaMonitoresView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        monitores = (
            PerfilMonitor.objects
            .filter(aprobado=True)
            .select_related('usuario')
            .prefetch_related('materias', 'disponibilidades')
        )
        materia_id = request.GET.get('materia')
        nombre     = request.GET.get('nombre', '').strip()
        modalidad  = request.GET.get('modalidad', '').strip()

        if materia_id:
            monitores = monitores.filter(materias__id=materia_id)
        if nombre:
            monitores = (
                monitores.filter(usuario__first_name__icontains=nombre) |
                monitores.filter(usuario__last_name__icontains=nombre)
            )
        if modalidad:
            monitores = monitores.filter(
                disponibilidades__modalidad=modalidad
            ).distinct()

        return render(request, 'monitores/lista.html', {
            'monitores':   monitores.distinct(),
            'materias':    Materia.objects.all(),
            'notif_count': request.user.notificaciones.filter(leida=False).count(),
        })


class DetalleMonitorView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, pk):
        monitor = get_object_or_404(PerfilMonitor, pk=pk, aprobado=True)
        from apps.usuarios.models import PerfilDocente
        return render(request, 'monitores/detalle.html', {
            'monitor':           monitor,
            'materias_monitor':  monitor.materias.all(),
            'disponibilidades':  monitor.disponibilidades.filter(activo=True),
            'docentes':          PerfilDocente.objects.all().select_related('usuario'),
            'notif_count':       request.user.notificaciones.filter(leida=False).count(),
        })


class AprobarMonitorView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, pk):
        if request.user.rol != 'ADMINISTRADOR':
            messages.error(request, 'No tienes permisos para realizar esta acción.')
            return redirect('usuarios:dashboard')

        monitor = get_object_or_404(PerfilMonitor, pk=pk)
        accion  = request.POST.get('accion', 'aprobar')

        if accion == 'aprobar':
            from django.utils import timezone
            monitor.aprobado         = True
            monitor.aprobado_por     = request.user
            monitor.fecha_aprobacion = timezone.now()
            monitor.save()
            messages.success(
                request,
                f'Monitor {monitor.usuario.nombre_completo} aprobado correctamente.'
            )
        else:
            nombre = monitor.usuario.nombre_completo
            monitor.delete()
            messages.warning(request, f'Solicitud de {nombre} rechazada y eliminada.')

        return redirect('usuarios:dashboard')
