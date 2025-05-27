from django.db import models
from django.contrib.auth.models import User # Import User model
import uuid
import qrcode
from phonenumber_field.modelfields import PhoneNumberField
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils.text import slugify


class Evento(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.AutoField(primary_key=True)  # Mantén el ID numérico para evitar errores
    uuid_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events')
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True) # Allow blank initially
    fecha = models.DateTimeField()
    aforo = models.IntegerField()
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='eventos/', null=True, blank=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)  # New field
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New field
    created_at = models.DateTimeField(auto_now_add=True)  # Asegúrate de que esto esté definido
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)  # New field

    def get_absolute_url(self):
        return reverse("event:evento_detalle", kwargs={"slug": self.slug})
    
    
    def save(self, *args, **kwargs):
        generate_new_slug = False
        if not self.slug: # If slug is not set (e.g. new object)
            generate_new_slug = True
        elif self.pk: # If object exists, check if nombre changed
            try:
                old_instance = Evento.objects.get(pk=self.pk)
                if old_instance.nombre != self.nombre:
                    generate_new_slug = True
            except Evento.DoesNotExist: # Should not happen if self.pk exists, but good practice
                generate_new_slug = True
        
        if generate_new_slug:
            self.slug = slugify(self.nombre)
            original_slug = self.slug
            counter = 1
            # Ensure slug uniqueness, excluding current instance if it exists
            queryset = Evento.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            while queryset.exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
                queryset = Evento.objects.filter(slug=self.slug)
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)

        # Determine if QR code needs regeneration
        # Needs regeneration if it's a new event, slug has changed, or QR code doesn't exist
        needs_qr_regeneration = False
        if self.pk is None:  # New event
            needs_qr_regeneration = True
        else:
            old_instance = Evento.objects.get(pk=self.pk) # Fetch old instance to compare slug
            if old_instance.slug != self.slug: # Slug changed
                needs_qr_regeneration = True
        
        if not self.qr_code: # QR code doesn't exist
            needs_qr_regeneration = True

        # Call super().save() once to save slug and other fields
        # This ensures self.pk is available for new objects before QR generation
        # And that get_absolute_url uses the latest slug
        super().save(*args, **kwargs)

        if needs_qr_regeneration and self.slug: # Ensure slug is available for URL
            base_url = "https://localhost:8000"  # Consider using settings or Site framework
            # get_absolute_url will now use the potentially updated self.slug
            url = f"{base_url}{self.get_absolute_url()}" 

            # Generate the QR code
            qr_object = qrcode.make(url)
            buffer = BytesIO()
            qr_object.save(buffer, format='PNG')
            filename = f'qr_{self.slug}_{self.pk}.png' # Use current slug and pk

            # If qr_code already exists, delete the old one to prevent orphaned files
            if self.qr_code and hasattr(self.qr_code, 'delete'):
                self.qr_code.delete(save=False)
            
            self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
            
            # Save again only to update the qr_code field
            # Pass specific fields to update to avoid recursion and re-triggering full save logic
            kwargs_update = {'update_fields': ['qr_code']}
            # If we are inside a transaction that hasn't committed the initial save, 
            # a new super().save() might cause issues.
            # However, for this case, it's generally okay.
            super().save(*args, **kwargs_update)


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