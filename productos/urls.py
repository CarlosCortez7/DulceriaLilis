from django.urls import path
from . import views

urlpatterns = [
    # --- Vistas Generales (Home) ---
    path('', views.home, name='home'),

    # --- Carrito de Compras ---
    path('carrito/', views.cart_detail, name='cart_detail'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # --- Gestión de Productos (CRUD) ---
    path('productos/', views.modulo_productos, name='modulo_productos'),
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('productos/editar/<int:product_id>/', views.editar_producto, name='editar_producto'),
    path('eliminar_producto/<int:product_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('productos/exportar/', views.exportar_excel_productos, name='exportar_excel_productos'),
    
    # --- Utilidades ---
    path('autocomplete_sku/', views.autocomplete_sku, name='autocomplete_sku'),

    # --- Inventario ---
    path('inventario/', views.modulo_inventario, name='modulo_inventario'),
    path('inventario/buscar/', views.buscar_movimientos, name='buscar_movimientos'),
    path('inventario/editar/<int:id>/', views.editar_movimiento, name='editar_movimiento'),
    path('inventario/eliminar/<int:id>/', views.eliminar_movimiento, name='eliminar_movimiento'),
    
    # Esta es la nueva ruta que venía en la otra rama (integrada correctamente)
    path('inventario/exportar/', views.exportar_movimientos_excel, name='exportar_movimientos_excel'),

    # --- Categorías ---
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/buscar/', views.buscar_categorias, name='buscar_categorias'),
    path('categorias/nueva/', views.crear_categoria, name='crear_categoria'),
    path('categorias/editar/<int:id>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),
]