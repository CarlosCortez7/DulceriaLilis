from django.db import models
from django.conf import settings

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)                     
    rut = models.CharField(max_length=20, unique=True)            
    contacto = models.CharField(max_length=100, blank=True, null=True)  
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=50, choices=[
        ('materia_prima', 'Materia Prima'),
        ('insumo', 'Insumo'),
        ('servicio', 'Servicio'),
        ('otros', 'Otros'),
    ])
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

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
        settings.AUTH_USER_MODEL,  # 🔹 Usa tu modelo Usuario personalizado
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
