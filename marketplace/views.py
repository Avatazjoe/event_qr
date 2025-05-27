from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.urls import reverse_lazy # Not strictly needed here if get_absolute_url is used

from .models import Product
from .forms import ProductForm
# from users.models import Activity # If activity logging was to be implemented


class ProductListView(ListView):
    model = Product
    template_name = 'marketplace/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        # Optimize by selecting related seller if seller info is used in template
        return Product.objects.select_related('seller').order_by('-created_at')


class ProductDetailView(DetailView):
    model = Product
    template_name = 'marketplace/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        # Optimize by selecting related seller if seller info is used in template
        return Product.objects.select_related('seller')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['meta_title'] = f"{product.name} - Marketplace | Event QR"
        
        description_text = getattr(product, 'description', '')
        if description_text:
            description_text = description_text[:120] + "..." if len(description_text) > 120 else description_text
            
        context['meta_description'] = f"Buy {product.name} for ${product.price}. {description_text}"
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'marketplace/create_product.html'
    # success_url is automatically handled by get_absolute_url on the Product model

    def form_valid(self, form):
        form.instance.seller = self.request.user
        # The Product model's save method handles slug generation.
        # Activity logging would go here if implemented:
        # self.object = form.save() # Save first to get the object
        # Activity.objects.create(...)
        return super().form_valid(form)

# Placeholder for edit_product (ProductUpdateView) and delete_product (ProductDeleteView)
# class ProductUpdateView(LoginRequiredMixin, UpdateView):
#     model = Product
#     form_class = ProductForm
#     template_name = 'marketplace/edit_product.html' # Create this template
#     slug_field = 'slug'
#     slug_url_kwarg = 'slug'

#     def get_queryset(self):
#         # Ensure only the seller can edit their product
#         return Product.objects.filter(seller=self.request.user)

# class ProductDeleteView(LoginRequiredMixin, DeleteView):
#     model = Product
#     template_name = 'marketplace/delete_product_confirm.html' # Create this template
#     success_url = reverse_lazy('marketplace:product_list')
#     slug_field = 'slug'
#     slug_url_kwarg = 'slug'

#     def get_queryset(self):
#         # Ensure only the seller can delete their product
#         return Product.objects.filter(seller=self.request.user)
