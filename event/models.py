from django.db import models
import uuid
import qrcode
from phonenumber_field.modelfields import PhoneNumberField
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse


class Evento(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.AutoField(primary_key=True)  # Mantén el ID numérico para evitar errores
    uuid_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=200)
    fecha = models.DateTimeField()
    aforo = models.IntegerField()
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='eventos/', null=True, blank=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)  # New field
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New field
    created_at = models.DateTimeField(auto_now_add=True)  # Asegúrate de que esto esté definido
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)  # New field

    def get_absolute_url(self):
        return reverse("evento_detalle", kwargs={"evento_id": self.pk})
    
    
    def save(self, *args, **kwargs):
        # Save the event first to get the primary key
        super().save(*args, **kwargs)

        if not self.qr_code:
            # Generate the correct URL using the saved object's primary key
            base_url = "https://localhost:8000" #https://bedb61e9-32da-4a32-bb6a-c73727f76e32-00-w7mo7nsuhuf.picard.replit.dev"  # Change for deployment
            url = f"{base_url}{self.get_absolute_url()}"

            # Generate the QR code
            qr = qrcode.make(url)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')

            # Save the QR code to the qr_code field
            filename = f'qr_{self.pk}.png'  # Use pk instead of id
            self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

            # Save again to store the QR code
            super().save(*args, **kwargs)


class Entrada(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    comprador = models.CharField(max_length=255)
    email = models.EmailField()
    telefono = PhoneNumberField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, editable=False)  # Inherited from Evento
    hash = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    pagado = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Asegúrate de que esto esté definido

    def save(self, *args, **kwargs):
        if not self.precio:
            self.precio = self.evento.precio  # Inherit price from Evento
        if not self.qr_code:
            url = f"http://localhost:8000{reverse('entrada_detalle', kwargs={'hash': str(self.hash)})}"
            qr = qrcode.make(url)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            filename = f'qr_{self.hash}.png'
            self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        super(Entrada, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.comprador} - {self.evento.nombre}"

    def get_absolute_url(self):
        return reverse("entrada_detalle", kwargs={"hash": str(self.hash)})