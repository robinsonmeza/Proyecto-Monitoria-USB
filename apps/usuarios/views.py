from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('usuarios:dashboard')
        return render(request, 'usuarios/login.html')

    def post(self, request):
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('usuarios:dashboard')
        return render(request, 'usuarios/login.html', {
            'form_error': 'Correo o contraseña incorrectos.'
        })


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('usuarios:login')


class DashboardView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        user = request.user
        context = self._get_context(user)
        template = self._get_template(user.rol)
        return render(request, template, context)

    def _get_template(self, rol):
        templates = {
            'ESTUDIANTE':    'usuarios/dashboard_estudiante.html',
            'MONITOR':       'usuarios/dashboard_monitor.html',
            'DOCENTE':       'usuarios/dashboard_docente.html',
            'ADMINISTRADOR': 'usuarios/dashboard_admin.html',
        }
        return templates.get(rol, 'usuarios/dashboard_estudiante.html')

    def _get_context(self, user):
        from apps.monitores.models import PerfilMonitor
        from apps.notificaciones.models import Notificacion

        context = {
            'notif_count': Notificacion.objects.filter(usuario=user, leida=False).count()
        }

        if user.rol == 'ESTUDIANTE':
            from apps.usuarios.models import PerfilDocente
            from apps.sesiones.models import DisponibilidadDocente
            try:
                context['perfil'] = user.perfil_estudiante
            except Exception:
                pass
            context['monitores'] = (
                PerfilMonitor.objects
                .filter(aprobado=True)
                .select_related('usuario')
                .prefetch_related('materias', 'disponibilidades')
            )
            # Docentes con al menos un horario activo publicado
            docentes_con_disp = (
                PerfilDocente.objects
                .filter(disponibilidades__activo=True)
                .distinct()
                .select_related('usuario')
                .prefetch_related('disponibilidades', 'materias')
            )
            context['docentes_tutoria'] = docentes_con_disp

        elif user.rol == 'MONITOR':
            try:
                pm = user.perfil_monitor
                from apps.solicitudes.models import SolicitudMonitoria
                context['perfil_monitor'] = pm
                context['solicitudes_pendientes'] = SolicitudMonitoria.objects.filter(
                    monitor=pm, estado='PENDIENTE'
                )
                context['disponibilidades'] = pm.disponibilidades.filter(activo=True)
            except Exception:
                pass

        elif user.rol == 'DOCENTE':
            try:
                from apps.sesiones.models import DisponibilidadDocente
                from apps.solicitudes.models import SolicitudTutoria
                from apps.monitores.models import Materia
                pd = user.perfil_docente
                context['perfil_docente']      = pd
                context['materias_docente']    = Materia.objects.all()
                context['disponibilidades']    = DisponibilidadDocente.objects.filter(
                    docente=pd, activo=True
                ).select_related('materia')
                context['tutorias_pendientes'] = SolicitudTutoria.objects.filter(
                    docente=pd, estado='PENDIENTE'
                ).select_related('estudiante__usuario', 'materia')
                context['monitores'] = (
                    PerfilMonitor.objects
                    .filter(materias__in=pd.materias.all(), aprobado=True)
                    .distinct()
                    .select_related('usuario')
                    .prefetch_related('materias')
                )
            except Exception:
                pass

        elif user.rol == 'ADMINISTRADOR':
            from apps.usuarios.models import PerfilEstudiante
            from apps.solicitudes.models import SolicitudMonitoria
            from apps.monitores.models import Materia
            context['stats'] = {
                'estudiantes':       PerfilEstudiante.objects.count(),
                'monitores_activos': PerfilMonitor.objects.filter(aprobado=True).count(),
                'solicitudes_activas': SolicitudMonitoria.objects.filter(estado='ACTIVO').count(),
                'materias':          Materia.objects.count(),
            }
            context['monitores_pendientes'] = (
                PerfilMonitor.objects
                .filter(aprobado=False)
                .select_related('usuario')
                .prefetch_related('materias')
            )

        return context
