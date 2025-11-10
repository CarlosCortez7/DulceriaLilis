from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
# --- CHOICES A NIVEL DE MÓDULO ---
ESTADO_CHOICES = [
    ('activo', 'Activo'),
    ('inactivo', 'Inactivo'),
]

MEDIDA_CHOICES = [
    ('unidad', 'Unidad'),
    ('ml', 'ML'),
    ('litro', 'Litro'),
    ('kg', 'KG'),
    ('gramo', 'Gramo'),
]

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    # --- Identificación ---
    sku = models.CharField(max_length=50, unique=True)
    ean_upc = models.CharField(max_length=50, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    marca = models.CharField(max_length=100, null=True, blank=True)
    modelo = models.CharField(max_length=100, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    # --- Unidades y Precios ---
    uom_compra = models.CharField(max_length=10, choices=MEDIDA_CHOICES, default='unidad')
    uom_venta = models.CharField(max_length=10, choices=MEDIDA_CHOICES, default='unidad')
    factor_conversion = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costo_estandar = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    impuesto_iva = models.DecimalField(max_digits=5, decimal_places=2, default=19.00)

    # --- Stock y Control ---
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)
    stock_maximo = models.IntegerField(null=True, blank=True)
    punto_reorden = models.IntegerField(null=True, blank=True)
    perishable = models.BooleanField(default=False)
    control_por_lote = models.BooleanField(default=False)
    control_por_serie = models.BooleanField(default=False)

    # --- Relaciones y Estado ---
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True, default='default/default_product.png')
    ficha_tecnica = models.FileField(upload_to='fichas/', null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')

    # --- Timestamps ---
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sku} - {self.nombre}"

class Recepcion(models.Model):
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

class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.IntegerField()
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Campos adicionales del formulario
    documento_referencia = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    lote = models.CharField(max_length=50, blank=True, null=True)
    serie = models.CharField(max_length=100, blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_movimiento']
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"

    def __str__(self):
        return f"{self.tipo_movimiento} de {self.cantidad} x {self.producto.sku} el {self.fecha_movimiento.strftime('%Y-%m-%d')}"