from django.urls import path
# --- INICIO: IMPORTACIONES ACTUALIZADAS ---
from proveedores.views import (
    modulo_proveedores,
    editar_proveedor,
    eliminar_proveedor,
    exportar_excel_proveedores,
    asociar_producto_proveedor,
    desasociar_producto_proveedor,
    gestion_orden_compra,
    eliminar_orden_compra,
    agregar_detalle_orden,
    eliminar_detalle_orden,
    exportar_excel_ordenes
)
# --- FIN DE IMPORTACIONES ---

urlpatterns = [
    # ------------------------------------------------------------------
    # RUTA PRINCIPAL (Listar y Crear Proveedores)
    # ------------------------------------------------------------------
    path('modulo_proveedores/', modulo_proveedores, name='modulo_proveedores'),

    # ------------------------------------------------------------------
    # RUTA DE EDICIÓN (Proveedor)
    # ------------------------------------------------------------------
    path('editar_proveedor/<int:proveedor_id>/', editar_proveedor, name='editar_proveedor'),

    # ------------------------------------------------------------------
    # RUTAS PARA LA TAB 3 (Asociar/Desasociar Productos)
    # ------------------------------------------------------------------
    path('asociar_producto_proveedor/<int:proveedor_id>/', 
         asociar_producto_proveedor, 
         name='asociar_producto_proveedor'),
    
    path('desasociar_producto_proveedor/<int:asociacion_id>/', 
         desasociar_producto_proveedor, 
         name='desasociar_producto_proveedor'),

    # ------------------------------------------------------------------
    # RUTA DE ELIMINACIÓN (Proveedor principal)
    # ------------------------------------------------------------------
    path('eliminar_proveedor/<int:proveedor_id>/', eliminar_proveedor, name='eliminar_proveedor'),

    # ------------------------------------------------------------------
    # RUTA DE UTILIDAD (Exportar)
    # ------------------------------------------------------------------
    path('exportar_excel_proveedores/', exportar_excel_proveedores, name='exportar_excel_proveedores'),

    # ------------------------------------------------------------------
    # RUTA RAÍZ (Por si acaso)
    # ------------------------------------------------------------------
    path('', modulo_proveedores, name='proveedores_home'),
    
    
    # --- Rutas de Orden de Compra (Maestro) ---
    path('ordenes/', 
         gestion_orden_compra, 
         name='gestion_orden_compra'),
    
    path('ordenes/editar/<int:orden_id>/', 
         gestion_orden_compra, 
         name='editar_orden_compra'),
    
    path('ordenes/eliminar/<int:orden_id>/', 
         eliminar_orden_compra, 
         name='eliminar_orden_compra'),

    # --- Rutas de Detalle de OC ---
    path('ordenes/detalle/agregar/<int:orden_id>/', 
         agregar_detalle_orden, 
         name='agregar_detalle_orden'),
    
    path('ordenes/detalle/eliminar/<int:detalle_id>/', 
         eliminar_detalle_orden, 
         name='eliminar_detalle_orden'),

    # ------------------------------------------------------------------
    # RUTA DE UTILIDAD (Exportar Órdenes) (Req 3.v)
    # ------------------------------------------------------------------
    # <--- EDITADO: Ruta añadida para cumplir la rúbrica
    path('ordenes/exportar/', 
         exportar_excel_ordenes, 
         name='exportar_excel_ordenes'),

]