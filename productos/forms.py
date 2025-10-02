from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['id_interno', 'nombre', 'descripcion', 'categoria', 'marca', 'modelo', 
                  'unidad_compra', 'unidad_venta', 'precio_venta', 'imagen_url', 'stock_actual', 'estado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
            'imagen_url': forms.URLInput(attrs={'placeholder': 'URL de la imagen'}),
        }