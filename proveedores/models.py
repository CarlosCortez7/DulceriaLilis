from django.db import models
from django.conf import settings
from productos.models import Producto

ESTADO_CHOICES = [
    ('ACTIVO', 'Activo'),
    ('BLOQUEADO', 'Bloqueado'),
]

class Proveedor(models.Model):
    razon_social = models.CharField(max_length=100)
    nombre_fantasia = models.CharField(max_length=255, blank=True, null=True)
    rut_nif = models.CharField(max_length=20, unique=True)
    contacto_principal_nombre = models.CharField(max_length=100, blank=True, null=True)
    contacto_principal_email = models.EmailField(max_length=254, blank=True, null=True)
    contacto_principal_telefono = models.CharField(max_length=30, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    sitio_web = models.URLField(max_length=255, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    ciudad = models.CharField(max_length=128, blank=True, null=True)
    pais = models.CharField(max_length=64, default='Chile')
    condiciones_pago = models.CharField(max_length=100) # Requerido
    moneda = models.CharField(max_length=8, default='CLP') # Requerido
    tipo = models.CharField(max_length=50, choices=[
        ('materia_prima', 'Materia Prima'),
        ('insumo', 'Insumo'),
        ('servicio', 'Servicio'),
        ('otros', 'Otros'),
    ])
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    observaciones = models.TextField(blank=True, null=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.razon_social

class ProductoProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='productos_proveedor')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='proveedores_producto')
    
    costo = models.DecimalField(max_digits=18, decimal_places=6) # Costo al que este proveedor vende este producto
    lead_time_dias = models.IntegerField(default=7) # Tiempo de entrega
    min_lote = models.DecimalField(max_digits=18, decimal_places=6, default=1)
    descuento_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    preferente = models.BooleanField(default=False) # Si es el proveedor principal para este producto

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('proveedor', 'producto') # Evita duplicados

    def __str__(self):
        return f"{self.proveedor.razon_social} - {self.producto.nombre}"

class OrdenCompra(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('completada', 'Completada'),
    ]

    proveedor = models.ForeignKey(
        'Proveedor',
        on_delete=models.CASCADE,
        related_name='ordenes_compra'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Usa tu modelo Usuario personalizado
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_emitidas'
    )
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Orden #{self.id} - {self.proveedor.nombre}"
