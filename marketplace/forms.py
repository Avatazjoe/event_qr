from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image']
        # Seller will be set automatically from the logged-in user in the view
        # Timestamps (created_at, updated_at) are handled automatically by the model
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
