from django.db import models
from django.conf import settings
from productos.models import Producto
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, F, ExpressionWrapper
from django.core.validators import MinValueValidator  # <--- EDITADO: Importar validador
from decimal import Decimal                      # <--- EDITADO: Importar Decimal

# --- Tus modelos existentes ---

class Proveedor(models.Model):
    # ... (Tu modelo Proveedor existente, está perfecto) ...
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
    condiciones_pago = models.CharField(max_length=100)
    moneda = models.CharField(max_length=8, default='CLP')
    tipo = models.CharField(max_length=50, choices=[('materia_prima', 'Materia Prima'), ('insumo', 'Insumo'), ('servicio', 'Servicio'), ('otros', 'Otros')], default='otros')
    estado = models.CharField(max_length=20, choices=[('ACTIVO', 'Activo'), ('BLOQUEADO', 'Bloqueado')], default='ACTIVO')
    observaciones = models.TextField(blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.razon_social} ({self.rut_nif})"


class ProductoProveedor(models.Model):
    # ... (Tu modelo ProductoProveedor existente) ...
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='productos_proveedor')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='proveedores_producto')
    
    costo = models.DecimalField(
        max_digits=18, 
        decimal_places=6,
        validators=[MinValueValidator(Decimal('0.000001'))]  # <--- EDITADO
    ) 
    
    lead_time_dias = models.IntegerField(default=7, validators=[MinValueValidator(0)]) # <--- EDITADO (Asumo que 0 días es válido)
    
    min_lote = models.DecimalField(
        max_digits=18, 
        decimal_places=6, 
        default=1,
        validators=[MinValueValidator(Decimal('0.000001'))]  # <--- EDITADO
    )
    
    descuento_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    preferente = models.BooleanField(default=False) 
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('proveedor', 'producto') 

    def __str__(self):
        return f"{self.proveedor.razon_social} - {self.producto.nombre}"

# --- FIN de modelos existentes ---


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
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_emitidas'
    )
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

    def __str__(self):
        return f"Orden #{self.id} - {self.proveedor.razon_social}"

    def actualizar_total(self):
        subtotal_calculado = ExpressionWrapper(
            F('cantidad') * F('precio_unitario'),
            output_field=models.DecimalField(max_digits=10, decimal_places=2) 
        )
        
        suma_detalles = self.detalles_orden.aggregate(
            total_calculado=Sum(subtotal_calculado)
        )['total_calculado'] or 0.00
        
        self.total = suma_detalles
        self.save(update_fields=['total'])

class DetalleOrdenCompra(models.Model):
    orden = models.ForeignKey(
        OrdenCompra, 
        on_delete=models.CASCADE, 
        related_name='detalles_orden'
    )
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.SET_NULL,
        null=True
    )
    
    cantidad = models.DecimalField(
        max_digits=18, 
        decimal_places=6,
        validators=[MinValueValidator(Decimal('0.000001'))]  # <--- EDITADO
    )
    
    precio_unitario = models.DecimalField(
        max_digits=18, 
        decimal_places=6,
        validators=[MinValueValidator(Decimal('0.000001'))]  # <--- EDITADO
    ) 

    subtotal = models.DecimalField(max_digits=18, decimal_places=6, editable=False, default=0)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        # Agregué una comprobación por si el producto fue eliminado (SET_NULL)
        nombre_producto = self.producto.nombre if self.producto else "Producto Eliminado"
        return f"Detalle {self.id} de Orden {self.orden.id} - {nombre_producto}" # <--- EDITADO (Más seguro)

# --- SIGNALS (Están perfectos) ---
@receiver(post_save, sender=DetalleOrdenCompra)
def actualizar_total_oc_guardar(sender, instance, **kwargs):
    instance.orden.actualizar_total()

@receiver(post_delete, sender=DetalleOrdenCompra)
def actualizar_total_oc_eliminar(sender, instance, **kwargs):
    instance.orden.actualizar_total()