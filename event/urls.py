from django.urls import path
from . import views
from .views import entrada_detalle
from .views import estadisticas_evento
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),  # Ruta raíz para el home
    path('home/', views.home, name='home'),
    path('entrada/<uuid:hash>/', entrada_detalle, name='entrada_detalle'),
    path('event/<int:evento_id>/', views.evento_detalle, name='evento_detalle'),
    #path('tickets/<uuid:hash>/', views.verificar_entrada, name='ticket_detalle'),
    path('recepcion/', views.recepcion, name='recepcion'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('estadisticas/<int:evento_id>/', views.estadisticas_evento, name='estadisticas_evento'),  # Accepts integer evento_id
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)