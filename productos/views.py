from django.shortcuts import render, redirect, get_object_or_404
# Importa Q para búsquedas OR y los modelos necesarios
from django.db.models import Q, Sum
from .models import Producto, Categoria, MEDIDA_CHOICES, MovimientoInventario
from django.contrib import messages
from .forms import ProductoForm, MovimientoInventarioForm
from django.contrib.auth.decorators import login_required 
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
import openpyxl
from django.utils import timezone
from datetime import timedelta

# Create your views here.

def home(request):
    visitas = request.session.get('visitas', 0)
    request.session['visitas'] = visitas + 1
    productos = Producto.objects.filter(estado='activo').order_by('nombre')

    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES or None) # Añadir FILES para imágenes
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado correctamente.')
            return redirect('home')
        else:
             messages.error(request, 'Error al agregar el producto. Revisa el formulario.')
    else:
        form = ProductoForm()

    categorias = Categoria.objects.all()
    context = {
        'productos': productos,
        'form': form,
        'visitas': visitas,
        'categorias': categorias,
        'MEDIDA_CHOICES': MEDIDA_CHOICES
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
    """ Muestra la lista de productos (filtrada) y formulario. Responde a peticiones normales y AJAX para filtros dinámicos. """
    query = request.GET.get('q', '')
    productos = Producto.objects.all().select_related('categoria')

    if query:
        productos = productos.filter(
            Q(sku__icontains=query) | Q(nombre__icontains=query)
        )
    productos = productos.order_by('nombre')

    form = ProductoForm()
    categorias = Categoria.objects.all()

    # --- Contexto Base ---
    context = {
        'productos': productos,
        'categorias': categorias,
        'MEDIDA_CHOICES': MEDIDA_CHOICES,
        'form': form,
        'query': query,
        'edit_mode': False
    }
    # --- Lógica de Paginación ---
    paginator = Paginator(productos, 5)  
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
    # Si page_number no es un número, muestra la primera página
        page_obj = paginator.page(1)
    except EmptyPage:
    # Si la página está fuera de rango, muestra la última
        page_obj = paginator.page(paginator.num_pages)
    
    params=request.GET.copy()
    params.pop('page',None)

    querystring=params.urlencode()
    
    # --- Respuesta Diferenciada (Normal vs AJAX) ---
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Si es AJAX (desde el filtro de búsqueda), renderiza SOLO la tabla parcial
        html = render_to_string(
            template_name="productos/_product_list_partial.html",
            context={'productos': page_obj, 'page_obj': page_obj, 'querystring': querystring, 'request': request}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)
    else:
        # Si es una petición normal, renderiza la página completa
        return render(request, 'productos/modulo_productos.html', {**context, 'productos': page_obj, 'page_obj': page_obj, 'querystring': querystring})

@login_required
def modulo_inventario(request):
    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            sku = form.cleaned_data['sku_producto']
            try:
                producto = Producto.objects.get(sku=sku)
                movimiento = form.save(commit=False)
                movimiento.producto = producto
                movimiento.usuario = request.user

                # Actualizar stock del producto
                cantidad = form.cleaned_data['cantidad']
                if movimiento.tipo_movimiento == 'INGRESO':
                    producto.stock_actual += cantidad
                elif movimiento.tipo_movimiento == 'SALIDA':
                    if producto.stock_actual < cantidad:
                        messages.error(request, f"Stock insuficiente para {producto.nombre}. Stock actual: {producto.stock_actual}.")
                        # No guardar y redirigir
                        return redirect('modulo_inventario')
                    producto.stock_actual -= cantidad
                
                producto.save()
                movimiento.save()
                messages.success(request, f"Movimiento de '{movimiento.tipo_movimiento}' para '{producto.nombre}' registrado correctamente.")

            except Producto.DoesNotExist:
                messages.error(request, f"El producto con SKU '{sku}' no existe.")
        else:
            messages.error(request, "Error al registrar el movimiento. Revisa los datos del formulario.")
        return redirect('modulo_inventario')

    # --- Lógica para GET (Carga de página) ---
    form = MovimientoInventarioForm()
    
    # Datos para tarjetas de resumen
    today = timezone.now().date()
    movimientos_hoy = MovimientoInventario.objects.filter(fecha_movimiento__date=today).count()
    stock_total = Producto.objects.aggregate(total=Sum('stock_actual'))['total'] or 0
    productos_unicos = Producto.objects.count()

    # Historial de movimientos con paginación
    historial_movimientos = MovimientoInventario.objects.all().select_related('producto', 'usuario')
    paginator = Paginator(historial_movimientos, 10) # 10 movimientos por página
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'form': form,
        'movimientos': page_obj,
        'summary': {
            'movimientos_hoy': movimientos_hoy,
            'stock_total': stock_total,
            'productos_unicos': productos_unicos,
        }
    }    
    return render(request, 'productos/inventario.html', context)

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
    return render(request, 'modulo_productos.html', context)

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