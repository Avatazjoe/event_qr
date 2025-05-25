from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/new/', views.create_product, name='create_product'),
    # Add URLs for edit_product and delete_product later if implemented
    # path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    # path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),
]
