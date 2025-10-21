"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from productos.views import (home, agregar_producto, add_to_cart, remove_from_cart, cart_detail, modulo_productos, modulo_inventario)
from usuarios.views import (registrarse, iniciar_sesion, logout_view, recuperar_contraseña, crear_nueva_contraseña, modulo_usuarios)

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
    path('inventario/', modulo_inventario, name='modulo_inventario'),

    # Usuarios
    path("registrarse/", registrarse, name='registrarse'),
    path("recuperar_contraseña/", recuperar_contraseña, name='recuperar_contraseña'),
    path("crear_nueva_contraseña/", crear_nueva_contraseña, name='crear_nueva_contraseña'),
    path('usuarios/', modulo_usuarios, name='modulo_usuarios'),
    path("iniciar_sesion/", iniciar_sesion, name='iniciar_sesion'),
    path("logout/", logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)