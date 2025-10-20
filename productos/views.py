from django.shortcuts import render, redirect
from productos.models import Producto
from .forms import ProductoForm


# Create your views here.

def home(request):
    productos = Producto.objects.filter(estado='activo').order_by('nombre')

    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # recarga la página para mostrar el nuevo producto
    else:
        form = ProductoForm()

    return render(request, 'home.html', {'productos': productos, 'form': form})

def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductoForm()
    
    return render(request, 'agregar_producto.html', {'form': form})


def modulo_productos(request):
    return render(request, 'modulo_productos.html')

def modulo_inventario(request):
    return render(request, 'inventario.html')
