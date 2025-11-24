from django.urls import path
from . import views

urlpatterns = [
    # ------------------------------------------------------------------
    # RUTA PRINCIPAL (Listar y Crear Proveedores)
    # ------------------------------------------------------------------
    path('modulo_proveedores/', views.modulo_proveedores, name='modulo_proveedores'),

    # ------------------------------------------------------------------
    # RUTA RAÍZ DE LA APP (Redirige al módulo principal)
    # ------------------------------------------------------------------
    path('', views.modulo_proveedores, name='proveedores_home'),

    # ------------------------------------------------------------------
    # RUTA DE EDICIÓN (Proveedor)
    # ------------------------------------------------------------------
    path('editar_proveedor/<int:proveedor_id>/', views.editar_proveedor, name='editar_proveedor'),

    # ------------------------------------------------------------------
    # RUTAS PARA LA TAB 3 (Asociar/Desasociar Productos)
    # ------------------------------------------------------------------
    path('asociar_producto_proveedor/<int:proveedor_id>/', 
         views.asociar_producto_proveedor, 
         name='asociar_producto_proveedor'),
    
    path('desasociar_producto_proveedor/<int:asociacion_id>/', 
         views.desasociar_producto_proveedor, 
         name='desasociar_producto_proveedor'),

    # ------------------------------------------------------------------
    # RUTA DE ELIMINACIÓN (Proveedor principal)
    # ------------------------------------------------------------------
    path('eliminar_proveedor/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),

    # ------------------------------------------------------------------
    # RUTA DE UTILIDAD (Exportar Proveedores)
    # ------------------------------------------------------------------
    path('exportar_excel_proveedores/', views.exportar_excel_proveedores, name='exportar_excel_proveedores'),

    # ------------------------------------------------------------------
    # RUTAS DE ÓRDENES DE COMPRA (Maestro)
    # ------------------------------------------------------------------
    path('ordenes/', 
         views.gestion_orden_compra, 
         name='gestion_orden_compra'),
    
    path('ordenes/editar/<int:orden_id>/', 
         views.gestion_orden_compra, 
         name='editar_orden_compra'),
    
    path('ordenes/eliminar/<int:orden_id>/', 
         views.eliminar_orden_compra, 
         name='eliminar_orden_compra'),

    # ------------------------------------------------------------------
    # RUTAS DE DETALLE DE OC (Productos dentro de la orden)
    # ------------------------------------------------------------------
    path('ordenes/detalle/agregar/<int:orden_id>/', 
         views.agregar_detalle_orden, 
         name='agregar_detalle_orden'),
    
    path('ordenes/detalle/eliminar/<int:detalle_id>/', 
         views.eliminar_detalle_orden, 
         name='eliminar_detalle_orden'),

    # ------------------------------------------------------------------
    # RUTA DE UTILIDAD (Exportar Órdenes)
    # ------------------------------------------------------------------
    path('ordenes/exportar/', 
         views.exportar_excel_ordenes, 
         name='exportar_excel_ordenes'),
]