from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum
from .models import Producto, Categoria, MEDIDA_CHOICES, MovimientoInventario
from django.contrib import messages
from .forms import ProductoForm, MovimientoInventarioForm, CategoriaForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import openpyxl
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_GET
from usuarios.decorators import solo_inventario

# --- FILTRO DE SEGURIDAD PARA ADMIN ---
def solo_admin(user):
    """Retorna True solo si el usuario es Admin o Superusuario."""
    return user.is_authenticated and (user.rol == 'admin' or user.is_superuser)

# Create your views here.

def home(request):
    # Contador de visitas
    visitas = request.session.get('visitas', 0)
    request.session['visitas'] = visitas + 1

    # Productos activos
    productos = Producto.objects.filter(estado='activo').order_by('nombre')

    # Manejo del formulario de nuevo producto
    # Opcional: Si solo admin agrega desde home, protege este bloque
    if request.method == "POST":
        if not solo_admin(request.user):
             messages.warning(request, "No tienes permiso para realizar esta acción.")
             return redirect('home')
             
        form = ProductoForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado correctamente.')
            return redirect('home')
        else:
            messages.error(request, 'Error al agregar el producto. Revisa el formulario.')
    else:
        form = ProductoForm()

    # =====================
    # 🔹 PAGINADOR DINÁMICO
    # =====================
    page_size = request.GET.get('page_size')  # Número de productos por página
    if page_size:
        request.session['page_size'] = int(page_size)  # Guardamos en sesión
    else:
        page_size = request.session.get('page_size', 12)  # Valor por defecto: 12

    paginator = Paginator(productos, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Contexto para la plantilla
    categorias = Categoria.objects.all()
    context = {
        'productos': page_obj,             # Paginados
        'page_obj': page_obj,              # Objeto de paginación
        'page_size': int(page_size),       # Tamaño actual de página
        'form': form,
        'visitas': visitas,
        'categorias': categorias,
        'MEDIDA_CHOICES': MEDIDA_CHOICES,
    }

    return render(request, 'productos/home.html', context)

@login_required
@user_passes_test(solo_admin, login_url='/usuarios/sin_permiso/') # <--- PROTECCIÓN ADMIN
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado correctamente.')
            return redirect('modulo_productos')
        else:
            messages.error(request, 'Error al agregar el producto. Revisa el formulario.')
            return redirect('modulo_productos')
    else:
        return redirect('modulo_productos')

@login_required
def add_to_cart(request, product_id):
    producto = get_object_or_404(Producto, id=product_id)
    carrito = request.session.get('carrito', {})
    product_id_str = str(product_id)
    cantidad = carrito.get(product_id_str, 0) + 1

    carrito[product_id_str] = cantidad
    request.session['carrito'] = carrito
    request.session.modified = True
    messages.success(request, f'Producto "{producto.nombre}" agregado al carrito.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def remove_from_cart(request, product_id):
    carrito = request.session.get('carrito', {})
    product_id_str = str(product_id)

    if product_id_str in carrito:
        del carrito[product_id_str]
        request.session['carrito'] = carrito
        request.session.modified = True
        messages.success(request, "Producto eliminado del carrito.")
    return redirect('cart_detail')

def cart_detail(request):
    carrito = request.session.get('carrito', {})
    cart_items = []
    total_general = 0
    product_ids = carrito.keys()
    productos_en_carrito = Producto.objects.filter(id__in=product_ids).select_related('categoria')

    for producto in productos_en_carrito:
        product_id_str = str(producto.id)
        cantidad = carrito[product_id_str]
        subtotal = 0
        if producto.precio_venta:
            subtotal = producto.precio_venta * cantidad

        cart_items.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal,
        })
        total_general += subtotal

    return render(request, 'productos/cart_detail.html', {'cart_items': cart_items, 'total_general': total_general})

# --- GESTIÓN DE PRODUCTOS (SOLO ADMIN/INV PUEDE VER LISTA COMPLETA PARA GESTIONAR) ---
# Ajusta permisos si Bodega también necesita ver esto
@login_required
def modulo_productos(request):
    # Permitir acceso a Admin e Inventario (Bodega) para ver lista
    if not (solo_admin(request.user) or request.user.rol == 'inventario'):
         return redirect('sin_permiso')

    productos = Producto.objects.all().select_related('categoria')

    nombre = request.GET.get('nombre', '').strip()
    categoria_id = request.GET.get('categoria_id')
    precio_min = request.GET.get('precio', '').strip()

    if nombre:
        productos = productos.filter(nombre__icontains=nombre)
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if precio_min:
        try:
            productos = productos.filter(precio_venta__gte=float(precio_min))
        except ValueError:
            pass

    productos = productos.order_by('nombre')

    paginator = Paginator(productos, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categorias = Categoria.objects.all()
    form = ProductoForm()

    context = {
        'productos': page_obj,
        'categorias': categorias,
        'form': form,
        'page_obj': page_obj,
        'nombre': nombre,
        'categoria_id': categoria_id,
        'precio_min': precio_min,
        'es_admin': solo_admin(request.user), # Para ocultar botones de editar/eliminar en template
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('productos/_product_list_partial.html', context, request=request)
        return JsonResponse({'html_from_view': html})

    return render(request, 'productos/modulo_productos.html', context)


@login_required
@user_passes_test(solo_inventario, login_url='/usuarios/sin_permiso/')
def modulo_inventario(request):

    solo_lectura = request.user.rol == "finanzas"

    # --- POST ---
    if request.method == 'POST':
        if solo_lectura:
            messages.warning(request, "No tienes permisos para registrar movimientos.")
            return redirect('modulo_inventario')

        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            sku = form.cleaned_data['sku_producto'].strip().upper()
            cantidad = form.cleaned_data['cantidad']
            tipo = form.cleaned_data['tipo_movimiento']

            try:
                producto = Producto.objects.get(sku=sku)
            except Producto.DoesNotExist:
                messages.error(request, f" El producto con SKU '{sku}' no existe.")
                return redirect('modulo_inventario')

            movimiento = form.save(commit=False)
            movimiento.producto = producto
            movimiento.usuario = request.user

            if tipo == 'INGRESO':
                producto.stock_actual += cantidad
            elif tipo == 'SALIDA':
                if producto.stock_actual < cantidad:
                    messages.error(request, f"Stock insuficiente para '{producto.nombre}'.")
                    return redirect('modulo_inventario')
                producto.stock_actual -= cantidad

            movimiento.save()
            producto.save()
            messages.success(request, "Movimiento registrado correctamente.")
            return redirect('modulo_inventario')

        else:
            messages.error(request, "Error al registrar movimiento.")
            return redirect('modulo_inventario')

    # --- GET ---
    form = MovimientoInventarioForm()

    today = timezone.now().date()
    movimientos_hoy = MovimientoInventario.objects.filter(fecha_movimiento__date=today).count()
    stock_total = Producto.objects.aggregate(total=Sum('stock_actual'))['total'] or 0
    productos_unicos = Producto.objects.count()

    # ========= 🔥 NUEVO: SELECTOR DE TAMAÑO DE PÁGINA =========
    page_size = request.GET.get("page_size", request.session.get("inv_page_size", 10))
    try:
        page_size = int(page_size)
    except:
        page_size = 10

    request.session["inv_page_size"] = page_size
    # ===========================================================

    historial_movimientos = MovimientoInventario.objects.select_related("producto", "usuario").order_by("-fecha_movimiento")

    paginator = Paginator(historial_movimientos, page_size)
    page_number = request.GET.get("page", 1)

    try:
        movimientos_page = paginator.page(page_number)
    except PageNotAnInteger:
        movimientos_page = paginator.page(1)
    except EmptyPage:
        movimientos_page = paginator.page(paginator.num_pages)

    context = {
        "form": form,
        "movimientos": movimientos_page,
        "page_size": page_size,
        "page_size_options": [4, 10, 25, 50, 100],  # 👈 opciones disponibles
        "summary": {
            "movimientos_hoy": movimientos_hoy,
            "stock_total": stock_total,
            "productos_unicos": productos_unicos,
        },
        "solo_lectura": solo_lectura,
    }

    return render(request, "productos/inventario.html", context)


def buscar_movimientos(request):
    """Devuelve resultados filtrados del historial en formato JSON (AJAX)."""
    query = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    usuario = request.GET.get('usuario', '').strip()

    movimientos = MovimientoInventario.objects.select_related('producto', 'usuario').order_by('-fecha_movimiento')

    if query:
        movimientos = movimientos.filter(
            Q(producto__nombre__icontains=query) |
            Q(producto__sku__icontains=query) |
            Q(usuario__username__icontains=query)
        )

    if tipo:
        movimientos = movimientos.filter(tipo_movimiento=tipo)

    if usuario:
        movimientos = movimientos.filter(usuario__username=usuario)

    data = []
    for m in movimientos[:30]:  # limitar resultados
        data.append({
            'id': m.id,
            'fecha': m.fecha_movimiento.strftime('%Y-%m-%d %H:%M'),
            'tipo': m.tipo_movimiento,
            'producto': f"{m.producto.nombre} ({m.producto.sku})",
            'cantidad': m.cantidad,
            'usuario': m.usuario.username if m.usuario else 'Sistema',
            'doc': m.documento_referencia or '-',
        })
    return JsonResponse({'resultados': data})

@login_required
@user_passes_test(solo_inventario, login_url='/usuarios/sin_permiso/')
def editar_movimiento(request, id):
    movimiento = get_object_or_404(MovimientoInventario, id=id)
    form = MovimientoInventarioForm(request.POST or None, instance=movimiento)

    if request.method == 'POST':
        if form.is_valid():
            movimiento = form.save(commit=False)
            sku = form.cleaned_data.get('sku_producto')  # El SKU ingresado por el usuario
            try:
                producto = Producto.objects.get(sku=sku)
                movimiento.producto = producto
            except Producto.DoesNotExist:
                messages.error(request, f"No existe un producto con el SKU {sku}.")
                return render(request, 'productos/inventario_editar.html', {'form': form, 'movimiento': movimiento})
            
            movimiento.save()
            messages.success(request, "Movimiento actualizado correctamente.")
            return redirect('modulo_inventario')
        else:
            messages.error(request, "Error al actualizar el movimiento. Revisa los datos.")
    
    # Prellenar el SKU actual en el campo de formulario
    form.fields['sku_producto'].initial = movimiento.producto.sku

    return render(request, 'productos/inventario_editar.html', {'form': form, 'movimiento': movimiento})



@login_required
@user_passes_test(solo_inventario, login_url='/usuarios/sin_permiso/')
def eliminar_movimiento(request, id):
    movimiento = get_object_or_404(MovimientoInventario, id=id)
    if request.method == 'POST':
        movimiento.delete()
        messages.success(request, 'Movimiento eliminado correctamente.')
        return redirect('modulo_inventario')
    return render(request, 'productos/inventario_eliminar.html', {'movimiento': movimiento})


@login_required
@user_passes_test(solo_admin, login_url='/usuarios/sin_permiso/') # <--- PROTECCIÓN ADMIN
def eliminar_producto(request, product_id):
    """
    Elimina un producto específico. Requiere método POST para seguridad.
    """
    producto = get_object_or_404(Producto, id=product_id)
    if request.method == 'POST':
        nombre_producto = producto.nombre # Guardar nombre para el mensaje
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado correctamente.')
        # Redirigir a la lista de productos después de eliminar
        return redirect('modulo_productos')
    else:
        # Si es GET, no hacer nada y redirigir (más seguro)
        messages.warning(request, "La acción de eliminar debe hacerse mediante POST.")
        return redirect('modulo_productos')
    
@login_required
@user_passes_test(solo_admin, login_url='/usuarios/sin_permiso/') # <--- PROTECCIÓN ADMIN
def editar_producto(request, product_id):
    """
    Maneja la edición. Muestra el formulario RELLENO y guarda los cambios.
    Renderiza la MISMA plantilla que modulo_productos.
    """
    producto = get_object_or_404(Producto, id=product_id)
    form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado correctamente.')
            return redirect('modulo_productos')
        else:
            messages.error(request, 'Error al actualizar el producto. Revisa el formulario.')
            # Si hay error, volvemos a mostrar el form con los errores

    # Si es GET (o si el POST falló), mostramos el formulario relleno
    categorias = Categoria.objects.all()
    # Necesitamos pasar la lista completa de productos para la tabla
    todos_los_productos = Producto.objects.all().select_related('categoria').order_by('nombre')

    context = {
        'form': form, # El formulario (relleno o con errores)
        'producto': producto, # El producto que se está editando (útil para el título, etc.)
        'categorias': categorias,
        'MEDIDA_CHOICES': MEDIDA_CHOICES,
        'edit_mode': True, # Indicar que SÍ estamos editando
        'productos': todos_los_productos # Pasar la lista para la tabla de abajo
    }
    # Renderizar la MISMA plantilla
    return render(request, 'productos/modulo_productos.html', context)

@login_required
def exportar_excel_productos(request):
    """
    Genera un archivo Excel con la lista de productos, aplicando los filtros actuales.
    """
    # 1. Replicar la lógica de filtrado de la vista principal
    query = request.GET.get('q', '')
    productos = Producto.objects.all().select_related('categoria')

    if query:
        productos = productos.filter(
            Q(sku__icontains=query) | Q(nombre__icontains=query)
        )
    
    productos = productos.order_by('nombre')

    # 2. Crear el libro de Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Productos"

    # Escribir encabezados
    headers = [
        "SKU", "Nombre", "Descripción", "Categoría", "Marca", 
        "Precio Venta", "Costo Estándar", "Stock Mínimo", "Estado"
    ]
    ws.append(headers)

    # Escribir datos de cada producto
    for producto in productos:
        ws.append([
            producto.sku,
            producto.nombre,
            producto.descripcion,
            producto.categoria.nombre if producto.categoria else "",
            producto.marca,
            producto.precio_venta,
            producto.costo_estandar,
            producto.stock_minimo,
            producto.get_estado_display()
        ])

    # 3. Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lista_productos.xlsx'
    wb.save(response)

    return response

# crud de categorias
@login_required
@user_passes_test(solo_admin, login_url='/usuarios/sin_permiso/') # <--- PROTECCIÓN ADMIN
def listar_categorias(request):
    # === Guardar cantidad seleccionada en sesión ===
    if 'page_size' in request.GET:
        request.session['page_size'] = int(request.GET.get('page_size'))
    page_size = request.session.get('page_size', 5)

    # === Ordenar (asc / desc) ===
    sort_by = request.GET.get('sort', 'id')
    order = request.GET.get('order', 'asc')
    sort_field = sort_by
    if order == 'desc':
        sort_by = f'-{sort_by}'

    # === Filtro por búsqueda (si se usa el buscador) ===
    query = request.GET.get('q', '')
    categorias = Categoria.objects.all()
    if query:
        categorias = categorias.filter(nombre__icontains=query)

    # === Ordenar queryset ===
    categorias = categorias.order_by(sort_by)

    # === Paginación ===
    paginator = Paginator(categorias, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # === Contexto al template ===
    context = {
        'categorias': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'page_size': page_size,
        'sort_field': sort_field,
        'sort_order': order,
    }

    return render(request, 'productos/categorias/listar.html', context)

@login_required
@user_passes_test(solo_admin, login_url='/usuarios/sin_permiso/') # <--- PROTECCIÓN ADMIN
def buscar_categorias(request):
    """Filtra categorías por nombre en tiempo real"""
    query = request.GET.get('q', '').strip()
    categorias = Categoria.objects.all()

    if query:
        categorias = categorias.filter(nombre__icontains=query)

    # Renderiza el HTML parcial actualizado
    html = render_to_string(
        'productos/categorias/_category_list_partial.html',
        {'categorias': categorias, 'page_obj': None},
        request=request
    )
    return JsonResponse({'html': html})

@login_required
@user_passes_test(solo_admin, login_url='/usuarios/sin_permiso/') # <--- PROTECCIÓN ADMIN
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada correctamente.')
            return redirect('listar_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'productos/categorias/form.html', {'form': form, 'accion': 'Crear'})


@login_required
@user_passes_test(solo_admin, login_url='/usuarios/sin_permiso/') # <--- PROTECCIÓN ADMIN
def editar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría editada correctamente.')
            return redirect('listar_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'productos/categorias/form.html', {'form': form, 'accion': 'Editar'})

@login_required
@user_passes_test(solo_admin, login_url='/usuarios/sin_permiso/') # <--- PROTECCIÓN ADMIN
def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    categoria.delete()
    messages.success(request, 'Categoría eliminada correctamente.')
    return redirect('listar_categorias')

def autocomplete_sku(request):
    term = request.GET.get('term', '').strip()
    if not term:
        return JsonResponse([], safe=False)
    
    productos = Producto.objects.filter(nombre__icontains=term)[:10]  # los 10 primeros resultados
    results = []
    for p in productos:
        results.append({
            'label': f"{p.sku} - {p.nombre}",
            'value': p.sku
        })
    return JsonResponse(results, safe=False)

def exportar_movimientos_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Movimientos"

    # Encabezados completos
    ws.append([
        "Fecha Movimiento",
        "Tipo",
        "Producto",
        "SKU",
        "Cantidad",
        "Usuario",
        "Documento Ref.",
        "Lote",
        "Serie",
        "Fecha Vencimiento",
        "Observaciones"
    ])

    movimientos = MovimientoInventario.objects.select_related("producto", "usuario").order_by("-fecha_movimiento")

    for m in movimientos:
        ws.append([
            m.fecha_movimiento.strftime("%Y-%m-%d %H:%M") if m.fecha_movimiento else "-",
            m.get_tipo_movimiento_display(),
            m.producto.nombre,
            m.producto.sku,
            m.cantidad,
            m.usuario.username if m.usuario else "Sistema",
            m.documento_referencia or "-",
            m.lote or "-",
            m.serie or "-",
            m.fecha_vencimiento.strftime("%Y-%m-%d") if m.fecha_vencimiento else "-",
            m.observaciones or "-"
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename=\"movimientos_completo.xlsx\"'

    wb.save(response)
    return response