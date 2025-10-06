from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .form import FormularioTarea
from .models import Tareas
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .form import CustomLoginForm
from .form import UsuarioCreationForm


# Create your views here.

def home(request):
    return render(request, 'home.html')

def registrarse(request):
    if request.method == 'GET':
        form = UsuarioCreationForm()
    else:
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tareas')
    return render(request, 'registrarse.html', {'form': form})


@login_required
def tareas(request):
    tareas = Tareas.objects.filter(user=request.user, fecha_completado__isnull=True)
    return render(request, 'tareas.html', {'tareas': tareas})

@login_required
def tasks_completed(request):
    tareas = Tareas.objects.filter(user=request.user, fecha_completado__isnull=False).order_by('-fecha_completado')
    return render(request, 'tareas.html', {'tareas': tareas})

@login_required
def crear_tarea(request):
    if request.method == 'GET':
        return render(request, 'crear_tareas.html', {
            'form': FormularioTarea
        })
    else:
        try:
            form = FormularioTarea(request.POST)
            nueva_tarea = form.save(commit=False)
            nueva_tarea.user = request.user
            nueva_tarea.save()
            return redirect('tareas')
        except ValueError:
            return render(request, 'crear_tareas.html', {
                'form': FormularioTarea,
                'error': 'valida los datos'
            })

@login_required
def tareas_detalles(request, tarea_id):
    if request.method == 'GET':
        tarea = get_object_or_404(Tareas, pk=tarea_id, user=request.user)
        form = FormularioTarea(instance=tarea)
        return render(request, 'tareas_detalles.html', {'tarea': tarea, 'form': form})
    else:
        try:
            tarea = get_object_or_404(Tareas, pk=tarea_id, user=request.user)
            form = FormularioTarea(request.POST, instance=tarea)
            form.save()
            return redirect('tareas')
        except ValueError:
            return render(request, 'tareas_detalles.html', {'tarea': tarea, 'form': form, 'error': "Error actualizando detalles"})

@login_required
def tarea_completada(request, tarea_id):
    tarea = get_object_or_404(Tareas, pk=tarea_id, user=request.user)
    if request.method == 'POST':
        tarea.fecha_completado = timezone.now()
        tarea.save()
        return redirect('tareas')

@login_required
def tarea_eliminada(request, tarea_id):
    tarea = get_object_or_404(Tareas, pk=tarea_id, user=request.user)
    if request.method == 'POST':
        tarea.delete()
        return redirect('tareas')

def cerrar_sesion(request):
    logout(request)
    return redirect('home')

def iniciar_sesion(request):
    if request.method == 'GET':
        form = CustomLoginForm()
        return render(request, 'iniciar_sesion.html', {'form': form})
    else:
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('tareas')
        else:
            # form.errors ya tiene los mensajes de validación
            return render(request, 'iniciar_sesion.html', {
                'form': form,
                'error': 'Revisa los campos e intenta nuevamente'
            })
        
class CustomLoginView(LoginView):
    template_name = 'iniciar_sesion.html'
    authentication_form = CustomLoginForm