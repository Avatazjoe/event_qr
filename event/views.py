from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import Evento, Entrada
from .forms import EntradaForm, EventoForm
from users.models import Activity # Import Activity model


class EventoListView(ListView):
    model = Evento
    template_name = 'home.html' # Path relative to templates directory
    context_object_name = 'eventos'

    def get_queryset(self):
        # Optimized query: select related creator if accessed in template
        return Evento.objects.select_related('creator').order_by('fecha')


class EventoDetailView(DetailView):
    model = Evento
    template_name = 'evento_detalle.html' # Path relative to templates directory
    context_object_name = 'evento'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        # Optimized query: select related creator and prefetch related entradas
        return Evento.objects.select_related('creator').prefetch_related('entrada_set')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        context['form'] = EntradaForm()
        context['meta_title'] = f"{event.nombre} - Event QR"
        
        description_text = getattr(event, 'descripcion', '')
        if description_text:
            description_text = description_text[:120] + "..." if len(description_text) > 120 else description_text
        
        context['meta_description'] = f"Details for {event.nombre}. Join us on {event.fecha.strftime('%Y-%m-%d')} at {event.ubicacion}. {description_text}"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object() # Get the current Evento instance
        form = EntradaForm(request.POST)
        if form.is_valid():
            entrada = form.save(commit=False)
            entrada.evento = self.object
            entrada.precio = self.object.precio
            entrada.save()
            # Assuming Entrada model has get_absolute_url() that points to entrada_detalle
            return HttpResponseRedirect(entrada.get_absolute_url())
        else:
            # If form is invalid, re-render the page with the form and errors
            context = self.get_context_data(object=self.object, form=form)
            return self.render_to_response(context)


class EventoCreateView(LoginRequiredMixin, CreateView):
    model = Evento
    form_class = EventoForm
    template_name = 'event/crear_evento.html' # Path relative to templates directory
    success_url = reverse_lazy('users:dashboard') # Assuming 'dashboard' is in 'users' namespace

    def form_valid(self, form):
        form.instance.creator = self.request.user
        # The model's save method handles slug generation and QR code.
        # We need to save the object first to get an ID for the activity log.
        self.object = form.save() 

        # Log activity
        Activity.objects.create(
            user=self.request.user,
            activity_type='event_created',
            description=f'Created event: {self.object.nombre}',
            # Use the object's get_absolute_url which now uses slug
            content_object_url=self.object.get_absolute_url() 
        )
        return HttpResponseRedirect(self.get_success_url())


class EntradaDetailView(DetailView):
    model = Entrada
    template_name = 'entrada_detalle.html' # Path relative to templates directory
    context_object_name = 'entrada'
    # 'hash' is a UUIDField, not the PK. We use it like a slug.
    slug_field = 'hash' 
    slug_url_kwarg = 'hash'

    def get_queryset(self):
        # Optimized query: select related evento and its creator
        return Entrada.objects.select_related('evento__creator')


class RecepcionView(LoginRequiredMixin, TemplateView):
    template_name = 'recepcion.html' # Path relative to templates directory


class EstadisticasView(TemplateView): # LoginRequiredMixin can be added if needed
    template_name = 'estadisticas.html' # Path relative to templates directory

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Optimized: select_related for creator if event list shows creator details
        eventos = Evento.objects.select_related('creator').all()
        
        total_eventos = eventos.count()
        eventos_creados_ultimo_mes = eventos.filter(created_at__gte=timezone.now() - timedelta(days=30)).count() # Assuming created_at field
        total_entradas = Entrada.objects.count()
        entradas_pagadas = Entrada.objects.filter(pagado=True).count()
        entradas_sin_pagar = total_entradas - entradas_pagadas

        context.update({
            'eventos': eventos,
            'total_eventos': total_eventos,
            'eventos_creados_ultimo_mes': eventos_creados_ultimo_mes,
            'total_entradas': total_entradas,
            'entradas_pagadas': entradas_pagadas,
            'entradas_sin_pagar': entradas_sin_pagar,
        })
        return context


class EstadisticasEventoView(DetailView): # LoginRequiredMixin can be added if needed
    model = Evento
    template_name = 'estadisticas_evento.html' # Path relative to templates directory
    context_object_name = 'evento'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Evento.objects.select_related('creator')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evento = self.get_object()
        
        entradas_evento = Entrada.objects.filter(evento=evento)
        total_entradas_evento = entradas_evento.count()
        entradas_pagadas_evento = entradas_evento.filter(pagado=True).count()
        entradas_sin_pagar_evento = total_entradas_evento - entradas_pagadas_evento

        reservas_por_fecha = entradas_evento.values('created_at__date').annotate(total=Count('id')).order_by('created_at__date')
        pagos_por_fecha = entradas_evento.filter(pagado=True).values('created_at__date').annotate(total=Count('id')).order_by('created_at__date')

        context.update({
            'total_entradas_evento': total_entradas_evento,
            'entradas_pagadas_evento': entradas_pagadas_evento,
            'entradas_sin_pagar_evento': entradas_sin_pagar_evento,
            'reservas_por_fecha': [{'date': item['created_at__date'].strftime('%Y-%m-%d'), 'total': item['total']} for item in reservas_por_fecha],
            'pagos_por_fecha': [{'date': item['created_at__date'].strftime('%Y-%m-%d'), 'total': item['total']} for item in pagos_por_fecha],
        })
        return context


class VerificarEntradaView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # hash is passed as a kwarg from the URL
        entrada = get_object_or_404(Entrada.objects.select_related('evento'), hash=self.kwargs['hash'])
        return JsonResponse({
            'comprador': entrada.comprador,
            'pagado': entrada.pagado,
            'evento': entrada.evento.nombre,
            'precio': str(entrada.precio),
        })