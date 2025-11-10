from django import forms
from .models import Proveedor, ProductoProveedor, OrdenCompra, DetalleOrdenCompra # <-- Importar Detalle
from productos.models import Producto # <-- Importar Producto

# --- FORMULARIOS DE PROVEEDOR (Existentes) ---
class ProveedorForm(forms.ModelForm):

    email = forms.EmailField(
        label="Email General",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@proveedor.cl'})
    )
    
    contacto_principal_email = forms.EmailField(
        label="Email Contacto",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contacto@proveedor.cl'})
    )

    class Meta:
        model = Proveedor
        fields = [
            'razon_social', 'nombre_fantasia', 'rut_nif', 'contacto_principal_nombre',
            'contacto_principal_email', 'contacto_principal_telefono', 'telefono', 'email',
            'sitio_web', 'direccion', 'ciudad', 'pais', 'condiciones_pago',
            'moneda', 'tipo', 'estado', 'observaciones',
        ]
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Proveedor S.A.'}),
            'nombre_fantasia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ProveMax'}),
            'rut_nif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '76.123.456-K'}),
            'contacto_principal_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del contacto principal'}),
            'contacto_principal_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 2 2345 6789'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://proveedor.cl'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Av. Principal 123'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Santiago'}),
            'pais': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chile'}),
            'condiciones_pago': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '30 días crédito'}),
            'moneda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CLP / USD'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas u observaciones adicionales'}),
        }
    
    def clean_rut_nif(self):
        rut_nif = self.cleaned_data.get('rut_nif', '').strip()
        if not rut_nif:
            raise forms.ValidationError("El RUT/NIF es obligatorio.")
        
        # Comprueba si el RUT existe Y no pertenece a la instancia actual (para edición)
        existe = Proveedor.objects.filter(rut_nif__iexact=rut_nif).exclude(pk=self.instance.pk).exists()
        if existe:
            raise forms.ValidationError("Ya existe un proveedor con este RUT/NIF.")
        return rut_nif

class ProductoProveedorForm(forms.ModelForm):
    
    lead_time_dias = forms.IntegerField(
        label="Lead Time (días)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 7}),
        required=True
    )
    
    min_lote = forms.DecimalField(
        label="Lote Mínimo",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 1, 'step': '0.000001'}),
        required=True,
        decimal_places=6,
        max_digits=18
    )
    
    costo = forms.DecimalField(
        label="Costo",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '123.45', 'step': '0.000001'}),
        required=True,
        decimal_places=6,
        max_digits=18
    )

    class Meta:
        model = ProductoProveedor
        fields = [
            'costo', 
            'lead_time_dias', 
            'min_lote', 
            'descuento_pct', 
            'preferente'
        ]
        widgets = {
            'descuento_pct': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'preferente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# --- FIN FORMULARIOS DE PROVEEDOR ---


# --- INICIO ORDEN DE COMPRA ---

class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = [
            'proveedor',
            'estado',
        ]
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Asignamos 'pendiente' al crear
        if not self.instance.pk:
            self.fields['estado'].initial = 'pendiente'
            # Mejoramos el selector de proveedor (solo al crear)
            self.fields['proveedor'].queryset = Proveedor.objects.order_by('razon_social')
            self.fields['proveedor'].label_from_instance = lambda obj: f"{obj.razon_social} ({obj.rut_nif})"
        
        # Si estamos editando (la instancia ya existe),
        if self.instance.pk:
            del self.fields['proveedor']



# --- FORMULARIO 'DetalleOrdenCompraForm' ---
class DetalleOrdenCompraForm(forms.ModelForm):
    
    # Creamos un campo para seleccionar el producto DEL PROVEEDOR
    producto_proveedor = forms.ModelChoiceField(
        queryset=ProductoProveedor.objects.none(), # Se llenará en la vista
        label="Producto",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_producto_proveedor_select'})
    )

    class Meta:
        model = DetalleOrdenCompra
        fields = [
            'cantidad',
            'precio_unitario'
        ]
        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad', 'step': '0.01'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio (auto)', 'step': '0.000001', 'id': 'id_precio_unitario'}),
        }

    def __init__(self, *args, **kwargs):
        # Sacamos el 'proveedor' que nos pasará la vista
        proveedor = kwargs.pop('proveedor', None) 
        super().__init__(*args, **kwargs)

        if proveedor:
            # Filtramos el queryset para mostrar solo productos de ESE proveedor
            self.fields['producto_proveedor'].queryset = ProductoProveedor.objects.filter(
                proveedor=proveedor
            ).select_related('producto').order_by('producto__nombre')
            
            # Hacemos que el dropdown muestre el nombre del producto
            self.fields['producto_proveedor'].label_from_instance = lambda obj: f"{obj.producto.nombre} (SKU: {obj.producto.sku})"