from django import forms
from .models import Entrada, Evento

class EntradaForm(forms.ModelForm):
    class Meta:
        model = Entrada
        fields = ['comprador', 'email', 'telefono']

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nombre', 'fecha', 'aforo', 'descripcion', 'imagen', 'ubicacion', 'precio']
