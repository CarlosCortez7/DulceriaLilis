from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

ROL_CHOICES = [
    ('admin', 'Administrador'),
    ('compras', 'Operador de Compras'),
    ('inventario', 'Operador de Inventario'),
    ('produccion', 'Operador de Producción'),
    ('ventas', 'Operador de Ventas'),
    ('finanzas', 'Analista Financiero'),
]

def avatar_upload_path(instance, filename):
    return f'avatars/user_{instance.id}/{filename}'


class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    rol = models.CharField(max_length=50, choices=ROL_CHOICES)
    area_unidad = models.CharField(max_length=100, blank=True, null=True)
    mfa_habilitado = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default_user.png', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.rol})"