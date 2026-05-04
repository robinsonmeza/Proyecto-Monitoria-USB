from django.urls import path
from . import views

app_name = 'solicitudes'

urlpatterns = [
    # Monitorías
    path('',                          views.MisSolicitudesView.as_view(), name='lista'),
    path('nueva/<int:monitor_pk>/',   views.NuevaSolicitudView.as_view(), name='nueva'),

    # Tutorías (docente directo)
    path('tutoria/nueva/<int:docente_pk>/', views.NuevaTutoriaView.as_view(), name='nueva_tutoria'),
]
