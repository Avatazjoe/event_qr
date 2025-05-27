from django.shortcuts import render, get_object_or_404, redirect # Added redirect
from .models import Product, Order, OrderItem # Added Order and OrderItem
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required # Added login_required

# from django.urls import reverse_lazy
from django.contrib import messages # Added for messages

from .forms import ProductCreateForm # Changed from ProductForm to ProductCreateForm
# from users.models import Activity


def product_list(request):
    query = request.GET.get('q')
    # products_list = Product.objects.all() # Renaming to avoid conflict if 'products' is used for page object
    products_queryset = Product.objects.all().order_by('-created_at') # Get all products, ordered by newest first

    if query:
        products_queryset = products_queryset.filter(name__icontains=query)

    paginator = Paginator(products_queryset, 6)  # Show 6 products per page
    page_number = request.GET.get('page')

    try:
        products_page = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products_page = paginator.page(paginator.num_pages)

    return render(request, 'marketplace/product_list.html', {'products': products_page, 'query': query})

# New function-based product_detail view
def product_detail(request, product_id): # Or use a slug: product_slug
    product = get_object_or_404(Product, id=product_id)
    # You might want to add related products or other context here later
    return render(request, 'marketplace/product_detail.html', {'product': product})

# Commenting out the old Class-Based View for product creation
# class ProductCreateView(LoginRequiredMixin, CreateView):
#     model = Product
#     form_class = ProductForm # This would need to be ProductCreateForm now
#     template_name = 'marketplace/create_product.html'
#     # success_url is automatically handled by get_absolute_url on the Product model

#     def form_valid(self, form):
#         # form.instance.seller = self.request.user # Product model doesn't have seller
#         # The Product model's save method handles slug generation.
#         # Activity logging would go here if implemented:
#         # self.object = form.save() # Save first to get the object
#         # Activity.objects.create(...)
#         return super().form_valid(form)

@login_required # Ensure only logged-in users can create products
def product_create(request):
    if request.method == 'POST':
        form = ProductCreateForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            # If you need to associate the product with the user who created it:
            # Assuming you might add a 'creator' ForeignKey field to Product model later:
            # product.creator = request.user 
            product.save()
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('marketplace:product_detail', product_id=product.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductCreateForm()
    return render(request, 'marketplace/product_create.html', {'form': form, 'title': 'Create Product'})

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

# Basic Order System Views

@login_required
def create_order(request, product_id): # Simplified: order for a single product type
    product = get_object_or_404(Product, id=product_id)
    # This is a highly simplified order creation process
    # In a real app, you'd have a cart, then an order creation form
    
    # For now, let's assume quantity is 1
    quantity = 1 
    
    order = Order.objects.create(user=request.user)
    OrderItem.objects.create(order=order, product=product, price=product.price, quantity=quantity)
    
    # messages.success(request, 'Order created successfully!') # Optional
    # Typically redirect to an order detail page or payment page
    return redirect('marketplace:order_detail', order_id=order.id) 

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user) # Ensure user owns the order
    return render(request, 'marketplace/order_detail.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'marketplace/order_history.html', {'orders': orders})
