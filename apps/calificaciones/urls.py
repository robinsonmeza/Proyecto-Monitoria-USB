from django.urls import path
from . import views

app_name = 'calificaciones'

urlpatterns = [
    path('<int:solicitud_pk>/calificar/', views.CalificarView.as_view(),         name='calificar'),
    path('mis-calificaciones/',           views.MisCalificacionesView.as_view(), name='mis_calificaciones'),
]
