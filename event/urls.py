from django.urls import path
from . import views # views will now contain the CBVs
from django.conf import settings
from django.conf.urls.static import static

app_name = 'event'

urlpatterns = [
    path('', views.EventoListView.as_view(), name='home'),
    path('entrada/<uuid:hash>/', views.EntradaDetailView.as_view(), name='entrada_detalle'),
    path('event/<slug:slug>/', views.EventoDetailView.as_view(), name='evento_detalle'),
    path('recepcion/', views.RecepcionView.as_view(), name='recepcion'),
    path('estadisticas/', views.EstadisticasView.as_view(), name='estadisticas'),
    path('estadisticas/<slug:slug>/', views.EstadisticasEventoView.as_view(), name='estadisticas_evento'),
    path('crear_evento/', views.EventoCreateView.as_view(), name='crear_evento'),
    path('tickets/verificar/<uuid:hash>/', views.VerificarEntradaView.as_view(), name='verificar_entrada'), # Added path for VerificarEntradaView
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)