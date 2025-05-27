from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse_lazy # Changed to reverse_lazy for models
from django.utils.text import slugify

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=255) # Added slug field
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        generate_new_slug = False
        if not self.slug: # If slug is not set
            generate_new_slug = True
        elif self.pk: # If object exists, check if name changed
            try:
                old_instance = Product.objects.get(pk=self.pk)
                if old_instance.name != self.name:
                    generate_new_slug = True
            except Product.DoesNotExist:
                generate_new_slug = True # Should not happen if self.pk exists

        if generate_new_slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            # Ensure slug uniqueness, excluding current instance if it exists
            queryset = Product.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            while queryset.exists():
                self.slug = f'{base_slug}-{counter}'
                counter += 1
                queryset = Product.objects.filter(slug=self.slug)
                if self.pk: # Re-check queryset for the new slug
                    queryset = queryset.exclude(pk=self.pk)
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # Uses namespaced URL 'marketplace:product_detail'
        return reverse_lazy('marketplace:product_detail', kwargs={'slug': self.slug})
