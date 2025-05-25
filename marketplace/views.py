from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm
from django.urls import reverse_lazy

def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'marketplace/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'marketplace/product_detail.html', {'product': product})

@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            # Log activity for product creation
            # Activity.objects.create(
            #     user=request.user,
            #     activity_type='product_created', # Add this to Activity model choices if it doesn't exist
            #     description=f'Listed a new product: {product.name}',
            #     content_object_url=product.get_absolute_url()
            # )
            return redirect(product.get_absolute_url()) # Redirect to product detail page
    else:
        form = ProductForm()
    return render(request, 'marketplace/create_product.html', {'form': form})

# Placeholder for edit_product and delete_product views if needed later
# @login_required
# def edit_product(request, pk):
#     product = get_object_or_404(Product, pk=pk, seller=request.user)
#     if request.method == 'POST':
#         form = ProductForm(request.POST, request.FILES, instance=product)
#         if form.is_valid():
#             form.save()
#             return redirect(product.get_absolute_url())
#     else:
#         form = ProductForm(instance=product)
#     return render(request, 'marketplace/edit_product.html', {'form': form, 'product': product})

# @login_required
# def delete_product(request, pk):
#     product = get_object_or_404(Product, pk=pk, seller=request.user)
#     if request.method == 'POST': # Confirmation step
#         product.delete()
#         return redirect('product_list') # Or user's dashboard / product management page
#     return render(request, 'marketplace/delete_product_confirm.html', {'product': product})
