from django.urls import path
from . import views

app_name = 'mensajes'

urlpatterns = [
    path('',                               views.BandejaView.as_view(),      name='bandeja'),
    path('<int:solicitud_pk>/enviar/',     views.EnviarMensajeView.as_view(), name='enviar'),
]
