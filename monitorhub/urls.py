from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.usuarios.urls', namespace='usuarios')),
    path('monitores/', include('apps.monitores.urls', namespace='monitores')),
    path('solicitudes/', include('apps.solicitudes.urls', namespace='solicitudes')),
    path('sesiones/',      include('apps.sesiones.urls',      namespace='sesiones')),
    path('calificaciones/', include('apps.calificaciones.urls', namespace='calificaciones')),
    path('mensajes/', include('apps.mensajes.urls', namespace='mensajes')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
