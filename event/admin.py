from django.contrib import admin
from .models import Evento, Entrada


admin.site.register(Entrada)

class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'ubicacion', 'precio')

admin.site.register(Evento, EventoAdmin)