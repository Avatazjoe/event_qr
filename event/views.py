from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Evento, Entrada
from .forms import EntradaForm
from users.models import Activity # Import Activity model
from django.urls import reverse # To generate URLs

from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta


def home(request):
    eventos = Evento.objects.order_by('fecha')
    return render(request, 'home.html', {'eventos': eventos})  # Se eliminó el prefijo "templates/"

def entrada_detalle(request, hash):
    entrada = get_object_or_404(Entrada, hash=hash)
    return render(request, 'entrada_detalle.html', {'entrada': entrada})
    
def evento_detalle(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == "POST":
        form = EntradaForm(request.POST)
        if form.is_valid():
            entrada = form.save(commit=False)
            entrada.evento = evento
            entrada.precio = evento.precio  # Set price from Evento
            entrada.save()
            return redirect(entrada.get_absolute_url())
    else:
        form = EntradaForm()
    
    return render(request, 'evento_detalle.html', {'evento': evento, 'form': form})  # Se eliminó el prefijo "templates/"

@login_required
def recepcion(request):
    return render(request, 'recepcion.html')  # Se eliminó el prefijo "templates/"

def estadisticas(request):
    # Obtener todos los eventos
    eventos = Evento.objects.all()

    # Contar eventos y entradas
    total_eventos = eventos.count()
    eventos_creados_ultimo_mes = eventos.filter(fecha__gte=timezone.now() - timedelta(days=30)).count()
    total_entradas = Entrada.objects.count()
    entradas_pagadas = Entrada.objects.filter(pagado=True).count()
    entradas_sin_pagar = total_entradas - entradas_pagadas

    contexto = {
        'eventos': eventos,  # Lista de eventos para mostrar como thumbnails
        'total_eventos': total_eventos,
        'eventos_creados_ultimo_mes': eventos_creados_ultimo_mes,
        'total_entradas': total_entradas,
        'entradas_pagadas': entradas_pagadas,
        'entradas_sin_pagar': entradas_sin_pagar,
    }

    return render(request, 'estadisticas.html', contexto)



def estadisticas_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    
    # Event-specific statistics
    total_entradas_evento = Entrada.objects.filter(evento=evento).count()
    entradas_pagadas_evento = Entrada.objects.filter(evento=evento, pagado=True).count()
    entradas_sin_pagar_evento = total_entradas_evento - entradas_pagadas_evento

    # Time series data for reservations and payments
    reservas_por_fecha = Entrada.objects.filter(evento=evento).values('created_at__date').annotate(total=Count('id'))
    pagos_por_fecha = Entrada.objects.filter(evento=evento, pagado=True).values('created_at__date').annotate(total=Count('id'))

    # Format dates as strings
    reservas_por_fecha = [{'date': item['created_at__date'].strftime('%Y-%m-%d'), 'total': item['total']} for item in reservas_por_fecha]
    pagos_por_fecha = [{'date': item['created_at__date'].strftime('%Y-%m-%d'), 'total': item['total']} for item in pagos_por_fecha]

    contexto = {
        'evento': evento,
        'total_entradas_evento': total_entradas_evento,
        'entradas_pagadas_evento': entradas_pagadas_evento,
        'entradas_sin_pagar_evento': entradas_sin_pagar_evento,
        'reservas_por_fecha': reservas_por_fecha,
        'pagos_por_fecha': pagos_por_fecha,
    }
    return render(request, 'estadisticas_evento.html', contexto)
    
@login_required
def verificar_entrada(request, hash):
    entrada = get_object_or_404(Entrada, hash=hash)
    return JsonResponse({
        'comprador': entrada.comprador,
        'pagado': entrada.pagado,
        'evento': entrada.evento.nombre,
        'precio': str(entrada.precio),
    })

@login_required
def crear_evento(request):
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.creator = request.user  # Set the creator to the logged-in user
            evento.save() # Save the event to get an ID for the URL
            
            # Log activity
            Activity.objects.create(
                user=request.user,
                activity_type='event_created',
                description=f'Created event: {evento.nombre}',
                content_object_url=reverse('evento_detalle', kwargs={'evento_id': evento.id})
            )
            return redirect('dashboard')  # Redirect to the user's dashboard
    else:
        form = EventoForm()
    return render(request, 'event/crear_evento.html', {'form': form})