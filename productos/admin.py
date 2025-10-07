from django.contrib import admin
from .models import Categoria, Producto

# Definir el modelo inline para Producto
class ProductoInline(admin.TabularInline):
    model = Producto
    extra = 1  
    fields = ('id_interno', 'nombre', 'precio_venta', 'unidad_compra', 'unidad_venta')
    show_change_link = True  # Para mostrar el enlace a los productos existentes

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    ordering = ['nombre']
    inlines = [ProductoInline]  # Integrando el inline para mostrar productos relacionados

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id_interno', 'nombre', 'categoria', 'precio_venta', 'stock_actual', 'estado')
    search_fields = ('id_interno', 'nombre')
    list_filter = ('categoria', 'perecible', 'control_por_lote', 'estado')
    ordering = ['nombre']
    list_select_related = ('categoria',)
