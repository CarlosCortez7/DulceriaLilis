from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .form import CustomLoginForm
from .form import UsuarioCreationForm

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
            return redirect('home')
    return render(request, 'registrarse.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
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
            request.session.cycle_key()
            return redirect('home')
        else:
            return render(request, 'iniciar_sesion.html', {
                'form': form,
                'error': 'Revisa los campos e intenta nuevamente'
            })
        
class CustomLoginView(LoginView):
    template_name = 'iniciar_sesion.html'
    authentication_form = CustomLoginForm

def recuperar_contraseña(request):
    return render(request, 'recuperar_contraseña.html')

def crear_nueva_contraseña(request):
    return render(request, 'crear_nueva_contraseña.html')

def modulo_usuarios(request):
    return render(request, 'CRUD_usuarios.html')