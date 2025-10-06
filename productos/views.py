from django.shortcuts import render, redirect
from productos.models import Producto
from .forms import ProductoForm


# Create your views here.

def home(request):
    productos = Producto.objects.filter(estado='activo', stock_actual__gt=0).order_by('nombre')

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
