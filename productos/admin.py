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
    list_display = ('nombre', 'categoria', 'estado', 'unidad_medida')
    search_fields = ('nombre','estado', 'unidad_medida')
    list_filter = ('categoria', 'estado')

