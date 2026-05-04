from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View

from .models import DisponibilidadDocente
from apps.monitores.models import Materia


class AgregarDisponibilidadView(LoginRequiredMixin, View):
    """Docente agrega un bloque de disponibilidad para tutorías."""
    login_url = '/login/'

    def post(self, request):
        if request.user.rol != 'DOCENTE':
            messages.error(request, 'Solo los docentes pueden gestionar disponibilidad.')
            return redirect('usuarios:dashboard')

        try:
            perfil_docente = request.user.perfil_docente
        except Exception:
            messages.error(request, 'No se encontró perfil de docente.')
            return redirect('usuarios:dashboard')

        dia       = request.POST.get('dia_semana', '')
        hora_ini  = request.POST.get('hora_inicio', '')
        hora_fin  = request.POST.get('hora_fin', '')
        modalidad = request.POST.get('modalidad', 'PRESENCIAL')
        ubicacion = request.POST.get('ubicacion', '').strip()
        materia_pk = request.POST.get('materia', '')

        if not all([dia, hora_ini, hora_fin, modalidad]):
            messages.error(request, 'Completa todos los campos obligatorios.')
            return redirect('usuarios:dashboard')

        materia = None
        if materia_pk:
            materia = Materia.objects.filter(pk=materia_pk).first()

        DisponibilidadDocente.objects.create(
            docente=perfil_docente,
            dia_semana=dia,
            hora_inicio=hora_ini,
            hora_fin=hora_fin,
            modalidad=modalidad,
            ubicacion=ubicacion,
            materia=materia,
        )

        messages.success(request, 'Disponibilidad agregada correctamente.')
        return redirect('usuarios:dashboard')


class EliminarDisponibilidadView(LoginRequiredMixin, View):
    """Docente elimina un bloque de disponibilidad."""
    login_url = '/login/'

    def post(self, request, pk):
        if request.user.rol != 'DOCENTE':
            messages.error(request, 'Sin permisos.')
            return redirect('usuarios:dashboard')

        disp = get_object_or_404(
            DisponibilidadDocente, pk=pk, docente=request.user.perfil_docente
        )
        disp.delete()
        messages.success(request, 'Disponibilidad eliminada.')
        return redirect('usuarios:dashboard')
