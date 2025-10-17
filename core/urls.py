"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

# Importar vistas
from productos.views import home, agregar_producto, add_to_cart, remove_from_cart, cart_detail
from usuarios.views import (registrarse, iniciar_sesion, logout_view, tareas, tasks_completed, crear_tarea, tareas_detalles, tarea_completada, tarea_eliminada)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('compras/', include('compras.urls')),  

    # Productos y Carrito
    path("", home, name='home'),
    path("agregar_producto/", agregar_producto, name='agregar_producto'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('carrito/', cart_detail, name='cart_detail'),

    # Usuarios
    path("registrarse/", registrarse, name='registrarse'),
    path("tareas/", tareas, name='tareas'),
    path("tasks_completed/", tasks_completed, name='tasks_completed'),
    path("tareas/crear/", crear_tarea, name='crear_tarea'),
    path("tareas/<int:tarea_id>/", tareas_detalles, name='tareas_detalles'),
    path("tareas/<int:tarea_id>/completado", tarea_completada, name='tarea_completada'),
    path("tareas/<int:tarea_id>/eliminar", tarea_eliminada, name='tarea_eliminada'),

    path("iniciar_sesion/", iniciar_sesion, name='iniciar_sesion'),
    path("logout/", logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)