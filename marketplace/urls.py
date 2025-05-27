from django.urls import path
from .views import product_list, product_detail, product_create, create_order, order_detail, order_history # Updated imports

app_name = 'marketplace'

urlpatterns = [
    path('', product_list, name='product_list'), 
    path('product/<int:product_id>/', product_detail, name='product_detail'), 
    path('create/', product_create, name='create_product'), # Changed path and view
    # Order system URLs
    path('order/create/<int:product_id>/', create_order, name='create_order'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/', order_history, name='order_history'),
    # Add URLs for edit_product and delete_product later if implemented
    # path('product/<slug:slug>/edit/', views.ProductUpdateView.as_view(), name='edit_product'),
    # path('product/<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='delete_product'),
]
