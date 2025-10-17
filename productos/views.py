from django.shortcuts import render, redirect, get_object_or_404
from productos.models import Producto
from django.contrib import messages
from .forms import ProductoForm
from django.contrib.auth.decorators import login_required


# Create your views here.

def home(request):
    # Controlador de visitas usando sesiones
    visitas = request.session.get('visitas', 0)
    request.session['visitas'] = visitas + 1

    productos = Producto.objects.filter(estado='activo').order_by('nombre')

    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # recarga la página para mostrar el nuevo producto
    else:
        form = ProductoForm()

    return render(request, 'home.html', {'productos': productos, 'form': form, 'visitas': visitas})

def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductoForm()
    
    return render(request, 'agregar_producto.html', {'form': form})

@login_required
def add_to_cart(request, product_id):
    """
    Agrega un producto al carrito de compras almacenado en la sesión.
    """
    producto = get_object_or_404(Producto, id=product_id)
    # Obtener el carrito de la sesión, o un diccionario vacío si no existe
    carrito = request.session.get('carrito', {})
    # Convertimos el ID a string para usarlo como clave en el diccionario JSON de la sesión
    product_id_str = str(product_id)

    # Cantidad que habría en el carrito si se añade una unidad más
    cantidad = carrito.get(product_id_str, 0) + 1

    # Verificar si hay stock suficiente
    if producto.stock_actual >= cantidad:
        carrito[product_id_str] = cantidad
        # Guardar el carrito de vuelta en la sesión y marcarla como modificada
        request.session['carrito'] = carrito
        request.session.modified = True
        messages.success(request, f'Producto "{producto.nombre}" agregado al carrito.')
    else:
        messages.error(request, f'Stock insuficiente para "{producto.nombre}".')

    return redirect('home')

def remove_from_cart(request, product_id):
    """
    Elimina un producto del carrito de compras almacenado en la sesión.
    """
    # Obtener el carrito de la sesión
    carrito = request.session.get('carrito', {})
    product_id_str = str(product_id)

    # Verificar si el producto está en el carrito y eliminarlo
    if product_id_str in carrito:
        del carrito[product_id_str]
        
        # Guardar los cambios en la sesión y marcarla como modificada
        request.session['carrito'] = carrito
        request.session.modified = True
        messages.success(request, "Producto eliminado del carrito.")

    return redirect('home') # Redirigimos a home, podría ser a una página de carrito

def cart_detail(request):
    """
    Muestra el contenido del carrito de compras.
    """
    carrito = request.session.get('carrito', {})
    cart_items = []
    total_general = 0

    # Obtener los objetos Producto para los IDs en el carrito
    product_ids = carrito.keys()
    productos_en_carrito = Producto.objects.filter(id__in=product_ids)

    for producto in productos_en_carrito:
        product_id_str = str(producto.id)
        cantidad = carrito[product_id_str]
        subtotal = producto.precio * cantidad
        
        cart_items.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal,
        })
        total_general += subtotal

    return render(request, 'productos/cart_detail.html', {'cart_items': cart_items, 'total_general': total_general})
