from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    id_interno = models.CharField(max_length=30, unique=True)  # Código interno del producto
    codigo_barras = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Código de barras

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    marca = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)

    # Unidades y precios
    unidad_compra = models.CharField(max_length=20)
    unidad_venta = models.CharField(max_length=20)
    factor_conversion = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    impuesto_iva = models.DecimalField(max_digits=5, decimal_places=2, default=19.00)

    # Stock y control
    stock_minimo = models.IntegerField(default=0)
    stock_maximo = models.IntegerField(blank=True, null=True)
    punto_reorden = models.IntegerField(blank=True, null=True)
    perecible = models.BooleanField(default=False)
    control_por_lote = models.BooleanField(default=False)
    control_por_serie = models.BooleanField(default=False)

    # Soporte visual y técnico
    imagen_url = models.URLField(blank=True, null=True)
    ficha_tecnica_url = models.URLField(blank=True, null=True)

    # Derivados (solo lectura en vistas)
    stock_actual = models.IntegerField(default=0)
    alerta_bajo_stock = models.BooleanField(default=False)
    alerta_por_vencer = models.BooleanField(default=False)

     # Nuevo campo para controlar visibilidad
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')

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