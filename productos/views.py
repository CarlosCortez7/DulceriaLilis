from django.shortcuts import render, redirect, get_object_or_404
# Importa Q para búsquedas OR y los modelos necesarios
from django.db.models import Q
from .models import Producto, Categoria, MEDIDA_CHOICES # <-- Añadido Categoria y MEDIDA_CHOICES
from django.contrib import messages
from .forms import ProductoForm # Asumiendo que tienes un ProductoForm en forms.py
from django.contrib.auth.decorators import login_required 
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger

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

    # Necesitas pasar Categorias y Medidas si el form está en home.html también
    categorias = Categoria.objects.all()
    context = {
        'productos': productos,
        'form': form,
        'visitas': visitas,
        'categorias': categorias,
        'MEDIDA_CHOICES': MEDIDA_CHOICES
    }
    return render(request, 'home.html', context)

def agregar_producto(request):
    if request.method == 'POST':
        # Añadir request.FILES para manejar subida de archivos (imagen, ficha)
        form = ProductoForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado correctamente.')
            # Redirigir a la lista de productos
            return redirect('modulo_productos')
        else:
            messages.error(request, 'Error al agregar el producto. Revisa el formulario.')
            # Idealmente, volver a mostrar el formulario con errores en modulo_productos
            # Para simplificar, redirigimos
            return redirect('modulo_productos')
    else:
        # Si alguien intenta acceder a esta URL por GET, redirigir
        return redirect('modulo_productos')

    # Este render probablemente ya no se usa si el form está en modulo_productos.html
    # return render(request, 'agregar_producto.html', {'form': form})

@login_required
def add_to_cart(request, product_id):
    producto = get_object_or_404(Producto, id=product_id)
    carrito = request.session.get('carrito', {})
    product_id_str = str(product_id)
    cantidad = carrito.get(product_id_str, 0) + 1

    # TODO: Implementar lógica de cálculo y verificación de stock real
    carrito[product_id_str] = cantidad
    request.session['carrito'] = carrito
    request.session.modified = True
    messages.success(request, f'Producto "{producto.nombre}" agregado al carrito.')
    return redirect(request.META.get('HTTP_REFERER', 'home')) # Volver a la página anterior

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
    # Optimizar consulta con select_related
    productos_en_carrito = Producto.objects.filter(id__in=product_ids).select_related('categoria')

    for producto in productos_en_carrito:
        product_id_str = str(producto.id)
        cantidad = carrito[product_id_str]
        subtotal = 0
        if producto.precio_venta: # Verificar si hay precio
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
    # --- Lógica de Filtrado (igual que antes) ---
    query = request.GET.get('q', '')
    productos = Producto.objects.all().select_related('categoria') # Empezar con todos

    if query:
        productos = productos.filter(
            Q(sku__icontains=query) | Q(nombre__icontains=query)
        )
    productos = productos.order_by('nombre')

    # --- Lógica Formulario Agregar (solo para GET inicial o POST con error) ---
    # El POST real lo maneja 'agregar_producto'
    form = ProductoForm() # Siempre mostrar un form vacío aquí
    categorias = Categoria.objects.all()

    # --- Contexto Base ---
    context = {
        'productos': productos,
        'categorias': categorias,
        'MEDIDA_CHOICES': MEDIDA_CHOICES,
        'form': form,
        'query': query, # Pasar el query actual para mostrarlo en el input
        'edit_mode': False
    }
    # --- Lógica de Paginación ---
    paginator = Paginator(productos, 2)  # Mostrar 2 productos por página
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
    
    return render(request, 'modulo_productos.html', {**context, 'productos': page_obj, 'page_obj': page_obj, 'querystring': querystring})


    # --- Respuesta Diferenciada (Normal vs AJAX) ---
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Si es AJAX (desde el filtro de búsqueda), renderiza SOLO la tabla parcial
        html = render_to_string(
            template_name="productos/_product_list_partial.html", # Plantilla solo con el bucle y <tr>
            context={'productos': productos, 'request': request} # Pasar request si se usa en el parcial (ej. para botones)
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)
    else:
        # Si es una petición normal, renderiza la página completa
        return render(request, 'modulo_productos.html', context)

def modulo_inventario(request):
    return render(request, 'inventario.html') # Asume que tienes 'inventario.html'

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