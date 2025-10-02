<<<<<<< HEAD
from django.shortcuts import render
from .models import Producto

# Create your views here.
def productos(request):
    productos = Producto.objects.filter(user=request.user, fecha_completado__isnull=True)
    return render(request, 'productos.html', {'productos': productos})

=======
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
>>>>>>> e8be2a1 (semillas y modulo categoria + formularios)
