from django.db import models
from proveedores.models import Proveedor


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    id_interno = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_actual = models.IntegerField(default=0)
    sku = models.CharField(max_length=50, unique=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    imagen_url = models.ImageField(upload_to='productos/', null=True, blank=True, default='productos/default_product.png')
    fecha_vencimiento = models.DateField(null=True, blank=True)
     # Nuevo campo para controlar visibilidad
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    MEDIDA_CHOICES = [
        ('unidad', 'Unidad'),
        ('ml', 'ML'),('litro', 'Litro'),
        ('kg', 'KG'),('gramo', 'Gramo'),
    ]
    unidad_medida = models.CharField(max_length=10, choices=MEDIDA_CHOICES, default='unidad')

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.id_interno} - {self.nombre}"
    
class Recepcion(models.Model):
    # Definición de campos de la recepcion
    numero_recepcion = models.CharField(max_length=50)
    fecha_recepcion = models.DateTimeField()

    def __str__(self):
        return f"Recepcion {self.numero_recepcion}"


class DetalleRecepcion(models.Model):
    recepcion = models.ForeignKey(Recepcion, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_recibida = models.IntegerField()

    def __str__(self):
        return f"Detalle de Recepcion - Producto {self.producto.nombre}"