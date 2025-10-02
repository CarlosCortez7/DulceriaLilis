from django.db import models
from proveedores.models import Proveedor
from productos.models import Producto
from usuarios.models import Usuario
# hace referencia al usuario que solicita la compra
class SolicitudCompra(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    solicitado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField()
    fecha_solicitud = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('recibida', 'Recibida'),
    ], default='pendiente')
    observaciones = models.TextField(blank=True, null=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.estado}"


class RecepcionCompra(models.Model):
    solicitud = models.ForeignKey(SolicitudCompra, on_delete=models.CASCADE)
    recibido_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha_recepcion = models.DateField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recepción de {self.solicitud.producto.nombre} - {self.fecha_recepcion}"



class DetalleRecepcion(models.Model):
    recepcion = models.ForeignKey(RecepcionCompra, on_delete=models.CASCADE)
    cantidad_recibida = models.PositiveIntegerField()
    estado_producto = models.CharField(max_length=50, choices=[
        ('bueno', 'Bueno'),
        ('dañado', 'Dañado'),
        ('incompleto', 'Incompleto'),
    ])
    lote = models.CharField(max_length=50, blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.recepcion.solicitud.producto.nombre} - {self.estado_producto}"
    
class DetalleSolicitud(models.Model):
    solicitud = models.ForeignKey('SolicitudCompra', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"