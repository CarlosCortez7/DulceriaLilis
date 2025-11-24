from django.urls import path
from . import views
<<<<<<< HEAD
=======
from productos.views import (agregar_producto, add_to_cart, remove_from_cart, cart_detail, modulo_productos, eliminar_producto, editar_producto, modulo_inventario, exportar_excel_productos, exportar_movimientos_excel)
>>>>>>> origin/feature/integracion-CARLOSNICO

urlpatterns = [
    # --- Vistas Generales (Home) ---
    path('', views.home, name='home'),

    # --- Carrito de Compras ---
    path('carrito/', views.cart_detail, name='cart_detail'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

<<<<<<< HEAD
    # --- Gestión de Productos (CRUD) ---
    path('productos/', views.modulo_productos, name='modulo_productos'),
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('productos/editar/<int:product_id>/', views.editar_producto, name='editar_producto'),
    path('eliminar_producto/<int:product_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('productos/exportar/', views.exportar_excel_productos, name='exportar_excel_productos'),
    
    # --- Utilidades ---
=======
    #productos
    path("agregar_producto/", agregar_producto, name='agregar_producto'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('carrito/', cart_detail, name='cart_detail'),
    path('productos/', modulo_productos, name='modulo_productos'),
    path('eliminar_producto/<int:product_id>/', eliminar_producto, name='eliminar_producto'),
    path('productos/editar/<int:product_id>/', editar_producto, name='editar_producto'),
    path('productos/exportar/', exportar_excel_productos, name='exportar_excel_productos'),

    #inventario
    path('inventario/', views.modulo_inventario, name='modulo_inventario'),#listo
>>>>>>> origin/feature/integracion-CARLOSNICO
    path('autocomplete_sku/', views.autocomplete_sku, name='autocomplete_sku'),

    # --- Inventario ---
    path('inventario/', views.modulo_inventario, name='modulo_inventario'),
    path('inventario/buscar/', views.buscar_movimientos, name='buscar_movimientos'),
    path('inventario/editar/<int:id>/', views.editar_movimiento, name='editar_movimiento'),
    path('inventario/eliminar/<int:id>/', views.eliminar_movimiento, name='eliminar_movimiento'),
<<<<<<< HEAD
=======
    path('inventario/buscar/', views.buscar_movimientos, name='buscar_movimientos'),# listo
    path('inventario/buscar/', views.buscar_movimientos, name='buscar_movimientos'),
    path("exportar-excel/", exportar_movimientos_excel, name="exportar_excel"),

>>>>>>> origin/feature/integracion-CARLOSNICO

    # --- Categorías ---
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/buscar/', views.buscar_categorias, name='buscar_categorias'),
    path('categorias/nueva/', views.crear_categoria, name='crear_categoria'),
    path('categorias/editar/<int:id>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),
]