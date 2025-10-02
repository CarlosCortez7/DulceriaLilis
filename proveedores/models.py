from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)                     # Nombre del proveedor
    rut = models.CharField(max_length=20, unique=True)            # RUT o identificación fiscal
    contacto = models.CharField(max_length=100, blank=True, null=True)  # Persona de contacto
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=50, choices=[
        ('materia_prima', 'Materia Prima'),
        ('insumo', 'Insumo'),
        ('servicio', 'Servicio'),
        ('otros', 'Otros'),
    ])
    activo = models.BooleanField(default=True)                    # ¿Está habilitado para compras?
    observaciones = models.TextField(blank=True, null=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre