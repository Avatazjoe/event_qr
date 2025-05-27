from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'), # Changed to slug
    path('product/new/', views.ProductCreateView.as_view(), name='create_product'),
    # Add URLs for edit_product and delete_product later if implemented
    # path('product/<slug:slug>/edit/', views.ProductUpdateView.as_view(), name='edit_product'),
    # path('product/<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='delete_product'),
]
