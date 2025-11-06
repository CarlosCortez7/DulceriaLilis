from django.shortcuts import render, redirect, get_object_or_404
# Importa Q para búsquedas OR y los modelos necesarios
from django.db.models import Q, Sum
from .models import Producto, Categoria, MEDIDA_CHOICES, MovimientoInventario
from django.contrib import messages
from .forms import ProductoForm, MovimientoInventarioForm, CategoriaForm
from django.contrib.auth.decorators import login_required 
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
import openpyxl
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_GET


# Create your views here.

def home(request):
    # Contador de visitas
    visitas = request.session.get('visitas', 0)
    request.session['visitas'] = visitas + 1

    # Productos activos
    productos = Producto.objects.filter(estado='activo').order_by('nombre')

    # Manejo del formulario de nuevo producto
    if request.method == "POST":
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

# --- VISTA CORREGIDA ---
def modulo_productos(request):
    productos = Producto.objects.all().select_related('categoria')

    nombre = request.GET.get('nombre', '').strip()
    productos = productos.filter(categoria_id=categoria_id)
    precio_min = request.GET.get('precio', '').strip()

    if nombre:
        productos = productos.filter(nombre__icontains=nombre)
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if precio_min:
        productos = productos.filter(precio_venta__icontains=str(precio_min))

    productos = productos.order_by('nombre')

    paginator = Paginator(productos, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    params = request.GET.copy()
    params.pop('page', None)
    querystring = params.urlencode()

    categorias = Categoria.objects.all()
    form = ProductoForm()

    context = {
        'productos': page_obj,
        'categorias': categorias,
        'form': form,
        'page_obj': page_obj,
        'querystring': querystring,
        'nombre': nombre,
        'categoria_id': categoria_id,
        'precio_min': precio_min,
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('productos/_product_list_partial.html', context, request=request)
        return JsonResponse({'html_from_view': html})
    else:
        return render(request, 'productos/modulo_productos.html', context)


@login_required
def modulo_inventario(request):
    """
    Módulo de inventario: permite registrar movimientos (ingreso/salida/ajuste),
    actualizar el stock del producto y mostrar el historial con resumen diario.
    """
    # --- POST: Registrar movimiento ---
    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            sku = form.cleaned_data['sku_producto'].strip().upper()  # limpia y normaliza el SKU
            cantidad = form.cleaned_data['cantidad']
            tipo = form.cleaned_data['tipo_movimiento']

            try:
                producto = Producto.objects.get(sku=sku)
            except Producto.DoesNotExist:
                messages.error(request, f" El producto con SKU '{sku}' no existe.")
                return redirect('modulo_inventario')

            # Crear el movimiento sin guardar aún
            movimiento = form.save(commit=False)
            movimiento.producto = producto
            movimiento.usuario = request.user

            # --- Lógica de actualización de stock ---
            if tipo == 'INGRESO':
                producto.stock_actual += cantidad
                movimiento.save()
                producto.save()
                messages.success(request, f" Ingreso de {cantidad} unidades al producto '{producto.nombre}' registrado correctamente.")

            elif tipo == 'SALIDA':
                if producto.stock_actual < cantidad:
                    messages.error(request, f" Stock insuficiente para '{producto.nombre}'. Stock actual: {producto.stock_actual}.")
                    return redirect('modulo_inventario')
                producto.stock_actual -= cantidad
                movimiento.save()
                producto.save()
                messages.success(request, f" Salida de {cantidad} unidades del producto '{producto.nombre}' registrada correctamente.")

            elif tipo == 'AJUSTE':
                # En ajustes no alteramos el stock directamente (opcional)
                movimiento.save()
                messages.info(request, f" Movimiento de ajuste registrado para '{producto.nombre}'.")

            else:
                messages.warning(request, " Tipo de movimiento no reconocido.")

            return redirect('modulo_inventario')
        else:
            messages.error(request, " Error al registrar el movimiento. Revisa los datos del formulario.")
            return redirect('modulo_inventario')

    # --- GET: Carga de página ---
    form = MovimientoInventarioForm()

    # --- Tarjetas de resumen ---
    today = timezone.now().date()
    movimientos_hoy = MovimientoInventario.objects.filter(fecha_movimiento__date=today).count()
    stock_total = Producto.objects.aggregate(total=Sum('stock_actual'))['total'] or 0
    productos_unicos = Producto.objects.count()

    # --- Historial con paginación ---
    historial_movimientos = MovimientoInventario.objects.select_related('producto', 'usuario').order_by('-fecha_movimiento')
    paginator = Paginator(historial_movimientos, 10)
    page_number = request.GET.get('page')

    try:
        movimientos_page = paginator.page(page_number)
    except PageNotAnInteger:
        movimientos_page = paginator.page(1)
    except EmptyPage:
        movimientos_page = paginator.page(paginator.num_pages)

    # --- Contexto al template ---
    context = {
        'form': form,
        'movimientos': movimientos_page,
        'summary': {
            'movimientos_hoy': movimientos_hoy,
            'stock_total': stock_total,
            'productos_unicos': productos_unicos,
        },
    }

    return render(request, 'productos/inventario.html', context)



@login_required
def editar_movimiento(request, id):
    movimiento = get_object_or_404(MovimientoInventario, id=id)
    form = MovimientoInventarioForm(request.POST or None, instance=movimiento)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Movimiento actualizado correctamente.")
            return redirect('modulo_inventario')
        else:
            messages.error(request, "Error al actualizar el movimiento. Revisa los datos.")
    
    return render(request, 'productos/inventario_editar.html', {'form': form, 'movimiento': movimiento})


@login_required
def eliminar_movimiento(request, id):
    movimiento = get_object_or_404(MovimientoInventario, id=id)
    if request.method == 'POST':
        movimiento.delete()
        messages.success(request, 'Movimiento eliminado correctamente.')
        return redirect('modulo_inventario')
    return render(request, 'productos/inventario_eliminar.html', {'movimiento': movimiento})


@login_required
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