from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import SolicitudCompra, RecepcionCompra, DetalleRecepcion, DetalleSolicitud
from .forms import (SolicitudCompraForm,RecepcionCompraForm,DetalleRecepcionForm,DetalleSolicitudForm,)

# --- INLINES ---
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


# --- ACCIONES PERSONALIZADAS ---
@admin.action(description="Marcar solicitudes como APROBADAS")
def marcar_aprobadas(modeladmin, request, queryset):
    queryset.update(estado="aprobada")


@admin.action(description="Marcar solicitudes como RECHAZADAS")
def marcar_rechazadas(modeladmin, request, queryset):
    queryset.update(estado="rechazada")


# --- ADMIN PRINCIPAL ---
@admin.register(SolicitudCompra)
class SolicitudCompraAdmin(admin.ModelAdmin):
    """Admin de SolicitudCompra con Inline, acciones personalizadas y validación."""
    form = SolicitudCompraForm
    list_display = ("producto", "proveedor", "cantidad", "estado", "fecha_solicitud")
    list_filter = ("estado", "proveedor")
    search_fields = ("producto__nombre", "proveedor__nombre")
    ordering = ["-fecha_solicitud"]
    list_select_related = ("producto", "proveedor")
    inlines = [DetalleSolicitudInline, RecepcionCompraInline]
    actions = [marcar_aprobadas, marcar_rechazadas]

    # --- VALIDACIÓN personalizada ---
    def save_model(self, request, obj, form, change):
        """Evita guardar solicitudes con cantidad 0 o negativa."""
        if obj.cantidad <= 0:
            raise ValidationError("La cantidad solicitada debe ser mayor a 0.")
        super().save_model(request, obj, form, change)

    # --- SCOPING / SEGURIDAD ---
    def get_queryset(self, request):
        """Restringe la vista según el rol del usuario."""
        qs = super().get_queryset(request)
        # El superusuario ve todo
        if request.user.is_superuser:
            return qs
        # Un usuario con rol limitado solo ve sus propias solicitudes
        if hasattr(request.user, "username"):
            return qs.filter(creado_por=request.user)
        return qs.none()


@admin.register(RecepcionCompra)
class RecepcionCompraAdmin(admin.ModelAdmin):
    """Admin de RecepcionCompra con Inline de detalles."""
    form = RecepcionCompraForm
    list_display = ("solicitud", "recibido_por", "fecha_recepcion")
    search_fields = ("solicitud__producto__nombre",)
    ordering = ["-fecha_recepcion"]
    list_select_related = ("solicitud", "recibido_por")
    inlines = [DetalleRecepcionInline]

    # --- VALIDACIÓN ---
    def save_model(self, request, obj, form, change):
        """Controla que la fecha de recepción no sea futura."""
        from datetime import date
        if obj.fecha_recepcion > date.today():
            raise ValidationError("La fecha de recepción no puede ser en el futuro.")
        super().save_model(request, obj, form, change)


@admin.register(DetalleRecepcion)
class DetalleRecepcionAdmin(admin.ModelAdmin):
    """Admin de DetalleRecepcion con filtros y búsqueda."""
    form = DetalleRecepcionForm
    list_display = ("recepcion", "cantidad_recibida", "estado_producto", "lote", "fecha_vencimiento")
    list_filter = ("estado_producto",)
    search_fields = ("lote",)
    ordering = ["-fecha_vencimiento"]
    list_select_related = ("recepcion",)


@admin.register(DetalleSolicitud)
class DetalleSolicitudAdmin(admin.ModelAdmin):
    """Admin de DetalleSolicitud."""
    form = DetalleSolicitudForm
    list_display = ("solicitud", "producto", "cantidad")
    search_fields = ("solicitud__id", "producto__nombre")
    ordering = ["solicitud"]
    list_select_related = ("solicitud", "producto")
