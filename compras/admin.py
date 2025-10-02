from django.contrib import admin
from .models import SolicitudCompra, RecepcionCompra, DetalleRecepcion, DetalleSolicitud
from .forms import (
    SolicitudCompraForm,
    RecepcionCompraForm,
    DetalleRecepcionForm,
    DetalleSolicitudForm,
)

# --- Inlines ---
class DetalleSolicitudInline(admin.TabularInline):
    """Permite gestionar los detalles de la solicitud desde el admin de SolicitudCompra"""
    model = DetalleSolicitud
    form = DetalleSolicitudForm
    extra = 0
    fields = ("producto", "cantidad")

class RecepcionCompraInline(admin.TabularInline):
    """Permite gestionar recepciones desde el admin de SolicitudCompra"""
    model = RecepcionCompra
    form = RecepcionCompraForm
    extra = 0
    fields = ("recibido_por", "observaciones")
    show_change_link = True

class DetalleRecepcionInline(admin.TabularInline):
    """Permite gestionar los detalles de la recepción desde el admin de RecepcionCompra"""
    model = DetalleRecepcion
    form = DetalleRecepcionForm
    extra = 0
    fields = ("cantidad_recibida", "estado_producto", "lote", "fecha_vencimiento")

# --- Acciones personalizadas ---
@admin.action(description="Marcar solicitudes como APROBADAS")
def marcar_aprobadas(modeladmin, request, queryset):
    queryset.update(estado="aprobada")

@admin.action(description="Marcar solicitudes como RECHAZADAS")
def marcar_rechazadas(modeladmin, request, queryset):
    queryset.update(estado="rechazada")

# --- Admin ---
@admin.register(SolicitudCompra)
class SolicitudCompraAdmin(admin.ModelAdmin):
    form = SolicitudCompraForm
    list_display = ("producto", "proveedor", "cantidad", "estado", "fecha_solicitud")
    list_filter = ("estado", "proveedor")
    search_fields = ("producto__nombre", "proveedor__nombre")
    inlines = [DetalleSolicitudInline, RecepcionCompraInline]
    actions = [marcar_aprobadas, marcar_rechazadas]

@admin.register(RecepcionCompra)
class RecepcionCompraAdmin(admin.ModelAdmin):
    form = RecepcionCompraForm
    list_display = ("solicitud", "recibido_por", "fecha_recepcion")
    search_fields = ("solicitud__producto__nombre",)
    inlines = [DetalleRecepcionInline]

@admin.register(DetalleRecepcion)
class DetalleRecepcionAdmin(admin.ModelAdmin):
    form = DetalleRecepcionForm
    list_display = ("recepcion", "cantidad_recibida", "estado_producto", "lote", "fecha_vencimiento")
    list_filter = ("estado_producto",)

@admin.register(DetalleSolicitud)
class DetalleSolicitudAdmin(admin.ModelAdmin):
    form = DetalleSolicitudForm
    list_display = ("solicitud", "producto", "cantidad")
    search_fields = ("solicitud__id", "producto__nombre")
