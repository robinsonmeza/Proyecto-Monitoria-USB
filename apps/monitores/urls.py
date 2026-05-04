from django.urls import path
from . import views

app_name = 'monitores'

urlpatterns = [
    path('',               views.ListaMonitoresView.as_view(),  name='lista'),
    path('<int:pk>/',      views.DetalleMonitorView.as_view(),  name='detalle'),
    path('<int:pk>/aprobar/', views.AprobarMonitorView.as_view(), name='aprobar'),
]
