"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from productos.views import (home, agregar_producto, add_to_cart, remove_from_cart, cart_detail, modulo_productos, modulo_inventario, eliminar_producto, editar_producto)
from usuarios.views import (registrarse, iniciar_sesion, logout_view, recuperar_contraseña, crear_nueva_contraseña, modulo_usuarios, eliminar_usuario, editar_usuario)
from proveedores.views import modulo_proveedores, guardar_proveedor, editar_proveedor, eliminar_proveedor, exportar_excel_proveedores

urlpatterns = [
    path('admin/', admin.site.urls),
    path('compras/', include('compras.urls')),   

    # Productos y Carrito
    path("", home, name='home'),
    path("agregar_producto/", agregar_producto, name='agregar_producto'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('carrito/', cart_detail, name='cart_detail'),
    path('productos/', modulo_productos, name='modulo_productos'),
    # Corrige la duplicidad de 'inventario/'
    path('inventario/', modulo_inventario, name='modulo_inventario'),
    path('eliminar_producto/<int:product_id>/', eliminar_producto, name='eliminar_producto'),
    path('productos/editar/<int:product_id>/', editar_producto, name='editar_producto'),

    # Rutas de Proveedores (NUEVAS Y MODIFICADAS)
    path('modulo_proveedores/', modulo_proveedores, name='modulo_proveedores'),
    path('guardar_proveedor/', guardar_proveedor, name='guardar_proveedor'),
    path('editar_proveedor/<int:proveedor_id>/', editar_proveedor, name='editar_proveedor'),
    path('eliminar_proveedor/<int:proveedor_id>/', eliminar_proveedor, name='eliminar_proveedor'),
    path('exportar_excel_proveedores/', exportar_excel_proveedores, name='exportar_excel_proveedores'),


    # Usuarios
    path("registrarse/", registrarse, name='registrarse'),
    path("recuperar_contraseña/", recuperar_contraseña, name='recuperar_contraseña'),
    path("crear_nueva_contraseña/", crear_nueva_contraseña, name='crear_nueva_contraseña'),
    path('usuarios/', modulo_usuarios, name='modulo_usuarios'),
    path("iniciar_sesion/", iniciar_sesion, name='iniciar_sesion'),
    path('eliminar_usuario/<int:user_id>/', eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/editar/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path("logout/", logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)