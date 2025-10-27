from django.urls import path
from . import views
from productos.views import (agregar_producto, add_to_cart, remove_from_cart, cart_detail, modulo_productos, eliminar_producto, editar_producto, modulo_inventario)

urlpatterns = [
    path('agregar/', views.agregar_producto, name='agregar_producto'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    #path('carrito/', views.cart_detail, name='cart_detail'),

    #productos
    path("agregar_producto/", agregar_producto, name='agregar_producto'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('carrito/', cart_detail, name='cart_detail'),
    path('productos/', modulo_productos, name='modulo_productos'),
    path('eliminar_producto/<int:product_id>/', eliminar_producto, name='eliminar_producto'),
    path('productos/editar/<int:product_id>/', editar_producto, name='editar_producto'),

    #inventario
    path('inventario/', modulo_inventario, name='modulo_inventario'),
]