from django.contrib import admin
from .models import Proveedor, OrdenCompra

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'tipo', 'activo')
    search_fields = ('nombre', 'rut', 'contacto')
    list_filter = ('tipo', 'activo')
    ordering = ('-creado',)
    date_hierarchy = 'creado'
    list_select_related = True

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'estado', 'total', 'fecha_emision', 'usuario')
    list_filter = ('estado', 'proveedor')
    search_fields = ('proveedor__nombre', 'usuario__username')
    ordering = ('-fecha_emision',)
    list_select_related = ('proveedor', 'usuario')  # 🚀 Evita consultas extra por cada fila