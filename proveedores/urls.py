from django.urls import path
from django.contrib.auth import views as auth_views
from proveedores.views import (modulo_proveedores, guardar_proveedor, editar_proveedor, eliminar_proveedor, exportar_excel_proveedores)

urlpatterns = [
    path('modulo_proveedores/', modulo_proveedores, name='modulo_proveedores'),
    path('guardar_proveedor/', guardar_proveedor, name='guardar_proveedor'),
    path('editar_proveedor/<int:proveedor_id>/', editar_proveedor, name='editar_proveedor'),
    path('eliminar_proveedor/<int:proveedor_id>/', eliminar_proveedor, name='eliminar_proveedor'),
    path('exportar_excel_proveedores/', exportar_excel_proveedores, name='exportar_excel_proveedores'),
]