from django.urls import path
from . import views

app_name = 'sesiones'

urlpatterns = [
    path('disponibilidad/agregar/',         views.AgregarDisponibilidadView.as_view(),   name='agregar_disponibilidad'),
    path('disponibilidad/<int:pk>/eliminar/', views.EliminarDisponibilidadView.as_view(), name='eliminar_disponibilidad'),
]
