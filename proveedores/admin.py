from django.contrib import admin
from .models import Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'tipo', 'activo')
    search_fields = ('nombre', 'rut', 'contacto')
    list_filter = ('tipo', 'activo')