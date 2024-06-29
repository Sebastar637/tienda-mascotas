from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['nombre', 'precio', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class MyForm(forms.Form):
    username = forms.CharField(label='Nombre de usuario', error_messages={'required': 'Este campo es obligatorio.'})
    email = forms.EmailField(label='Correo Electrónico')
    password = forms.CharField(label='Contraseña')
