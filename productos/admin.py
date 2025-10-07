from django.contrib import admin
from .models import Categoria, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    ordering = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id_interno', 'nombre', 'categoria', 'precio_venta', 'stock_actual', 'estado')
    search_fields = ('id_interno', 'nombre')
    list_filter = ('categoria', 'perecible', 'control_por_lote', 'estado')
    ordering = ['nombre']
    list_select_related = ('categoria',)
