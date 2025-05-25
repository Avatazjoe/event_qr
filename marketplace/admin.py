from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price', 'created_at')
    list_filter = ('seller', 'created_at')
    search_fields = ('name', 'description', 'seller__username')
