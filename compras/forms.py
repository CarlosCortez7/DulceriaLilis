from django import forms
from django.core.exceptions import ValidationError
from .models import SolicitudCompra, RecepcionCompra, DetalleRecepcion, DetalleSolicitud

class SolicitudCompraForm(forms.ModelForm):
    class Meta:
        model = SolicitudCompra
        fields = [
            'producto',
            'proveedor',
            'solicitado_por',
            'cantidad',
            'estado',
            'observaciones',
        ]
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data["cantidad"]
        if cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")
        return cantidad


class RecepcionCompraForm(forms.ModelForm):
    class Meta:
        model = RecepcionCompra
        fields = [
            'solicitud',
            'recibido_por',
            'observaciones',
        ]
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }


class DetalleRecepcionForm(forms.ModelForm):
    class Meta:
        model = DetalleRecepcion
        fields = [
            'recepcion',
            'cantidad_recibida',
            'estado_producto',
            'lote',
            'fecha_vencimiento',
        ]
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_cantidad_recibida(self):
        cantidad = self.cleaned_data["cantidad_recibida"]
        recepcion = self.cleaned_data.get("recepcion")  # Accedemos a 'recepcion' desde cleaned_data

        if cantidad <= 0:
            raise ValidationError("La cantidad recibida debe ser mayor a 0.")

        # Validación: no debe superar la cantidad solicitada
        if recepcion:  # Verifica que 'recepcion' no sea None
            if recepcion.solicitud:
                cantidad_solicitada = recepcion.solicitud.cantidad
                if cantidad > cantidad_solicitada:
                    raise ValidationError(
                        f"La cantidad recibida ({cantidad}) no puede ser mayor a la solicitada ({cantidad_solicitada})."
                    )
        else:
            raise ValidationError("Debe seleccionar una recepción válida.")

        return cantidad

class DetalleSolicitudForm(forms.ModelForm):
    class Meta:
        model = DetalleSolicitud
        fields = "__all__"

    def clean_cantidad(self):
        cantidad = self.cleaned_data["cantidad"]
        if cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")
        return cantidad