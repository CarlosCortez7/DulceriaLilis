from django.shortcuts import render, redirect, get_object_or_404
from productos.models import Producto
from django.contrib import messages
from .forms import ProductoForm
from django.contrib.auth.decorators import login_required


# Create your views here.

def home(request):
    visitas = request.session.get('visitas', 0)
    request.session['visitas'] = visitas + 1
    productos = Producto.objects.filter(estado='activo').order_by('nombre')

    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
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
    producto = get_object_or_404(Producto, id=product_id)
    carrito = request.session.get('carrito', {})
    product_id_str = str(product_id)
    cantidad = carrito.get(product_id_str, 0) + 1
    carrito[product_id_str] = cantidad
    request.session['carrito'] = carrito
    request.session.modified = True
    messages.success(request, f'Producto "{producto.nombre}" agregado al carrito.')
    return redirect('home')

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
    productos_en_carrito = Producto.objects.filter(id__in=product_ids)

    for producto in productos_en_carrito:
        product_id_str = str(producto.id)
        cantidad = carrito[product_id_str]
        subtotal = producto.precio_venta * cantidad 
        
        cart_items.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal,
        })
        total_general += subtotal

    return render(request, 'productos/cart_detail.html', {'cart_items': cart_items, 'total_general': total_general})

def modulo_productos(request):
    return render(request, 'modulo_productos.html')

def modulo_inventario(request):
    return render(request, 'inventario.html')