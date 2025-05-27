from django import forms
from .models import Product

class ProductCreateForm(forms.ModelForm): # Renamed from ProductForm
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image']
        # Seller will be set automatically from the logged-in user in the view
        # Timestamps (created_at, updated_at) are handled automatically by the model
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
