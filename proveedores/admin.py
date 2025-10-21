from django.contrib import admin
from .models import Proveedor, OrdenCompra, ProductoProveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'rut_nif', 'email', 'telefono', 'tipo', 'estado')
    search_fields = ('razon_social', 'nombre_fantasia', 'rut_nif', 'contacto_principal_nombre', 'email')
    list_filter = ('tipo', 'estado', 'pais')
    ordering = ('-creado',)
    date_hierarchy = 'creado'
    list_select_related = True

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'estado', 'total', 'fecha_emision', 'usuario')
    list_filter = ('estado', 'proveedor')
    search_fields = ('proveedor__razon_social', 'usuario__username')
    ordering = ('-fecha_emision',)
    list_select_related = ('proveedor', 'usuario')

@admin.register(ProductoProveedor)
class ProductoProveedorAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'producto', 'costo', 'lead_time_dias', 'preferente')
    list_filter = ('proveedor', 'producto', 'preferente')
    search_fields = ('proveedor__razon_social', 'producto__nombre', 'producto__sku')
    list_select_related = ('proveedor', 'producto')
    ordering = ('proveedor', 'producto')