from django.contrib import admin
from .models import Categoria, Producto

# Definir el modelo inline para Producto
class ProductoInline(admin.TabularInline):
    model = Producto
    extra = 1 
    fields = ('sku', 'nombre', 'estado', 'precio_venta', 'uom_venta')
    show_change_link = True

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    ordering = ['nombre']
    inlines = [ProductoInline]

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'categoria', 'estado', 'precio_venta', 'stock_minimo', 'perishable')
    search_fields = ('sku', 'nombre', 'estado', 'categoria__nombre')
    list_filter = ('categoria', 'estado', 'perishable', 'control_por_lote')