from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        # Incluir todos los campos editables del modelo
        fields = [
            'sku', 'ean_upc', 'nombre', 'descripcion', 'categoria', 'marca', 'modelo',
            'uom_compra', 'uom_venta', 'factor_conversion', 'precio_venta', 'costo_estandar',
            'impuesto_iva', 'stock_minimo', 'stock_maximo', 'punto_reorden', 'perishable',
            'control_por_lote', 'control_por_serie', 'imagen', 'ficha_tecnica', 'estado'
        ]
        # (Opcional) Puedes añadir widgets aquí para aplicar clases de Bootstrap
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder':'SKU-0001'}),
            'ean_upc': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder':'789...'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 2}),
            'categoria': forms.Select(attrs={'class': 'form-select mb-3'}),
            'marca': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'uom_compra': forms.Select(attrs={'class': 'form-select mb-3'}),
            'uom_venta': forms.Select(attrs={'class': 'form-select mb-3'}),
            'factor_conversion': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'costo_estandar': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'impuesto_iva': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'stock_maximo': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'punto_reorden': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'perishable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'control_por_lote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'control_por_serie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control mb-3'}),
            'ficha_tecnica': forms.ClearableFileInput(attrs={'class': 'form-control mb-3'}),
            'estado': forms.Select(attrs={'class': 'form-select mb-3'}),
        }