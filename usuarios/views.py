from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .form import CustomLoginForm, UsuarioCreationForm, UsuarioChangeForm
from .models import Usuario, ROL_CHOICES # Importar ROL_CHOICES si está definido en models.py
# Importar Q para búsquedas OR
from django.db.models import Q
# Importar para renderizar solo una parte (AJAX)
from django.template.loader import render_to_string
from django.http import JsonResponse

# Create your views here.

def home(request):
    """Vista simple para la página de inicio."""
    return render(request, 'home.html')

def registrarse(request):
    """Vista para el registro de nuevos usuarios."""
    if request.method == 'GET':
        form = UsuarioCreationForm()
    else:
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}! Registro exitoso.')
            return redirect('home')
        else:
             messages.error(request, 'Error en el registro. Revisa los datos.')
    return render(request, 'registrarse.html', {'form': form})

def logout_view(request):
    """Vista para cerrar sesión."""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('home')

def iniciar_sesion(request):
    """Vista para iniciar sesión."""
    if request.method == 'GET':
        form = CustomLoginForm()
        return render(request, 'iniciar_sesion.html', {'form': form})
    else:
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session.cycle_key() # Regenerar clave de sesión por seguridad
            messages.success(request, f'Bienvenido de nuevo, {user.username}.')
            return redirect('home')
        else:
            return render(request, 'iniciar_sesion.html', {
                'form': form,
            })

class CustomLoginView(LoginView):
    """Vista basada en clase para login (alternativa a la función)."""
    template_name = 'iniciar_sesion.html'
    authentication_form = CustomLoginForm

def recuperar_contraseña(request):
    """Vista placeholder para recuperar contraseña."""
    return render(request, 'recuperar_contraseña.html')

def crear_nueva_contraseña(request):
    """Vista placeholder para crear nueva contraseña."""
    return render(request, 'crear_nueva_contraseña.html')

@login_required
def modulo_usuarios(request):
    """
    Muestra la lista de usuarios (filtrada) y formulario para agregar.
    Responde a peticiones normales y AJAX para filtros dinámicos.
    """
    # --- Lógica de Filtrado ---
    query = request.GET.get('q', '')
    rol_filtro = request.GET.get('rol_filtro', '')
    estado_filtro = request.GET.get('estado_filtro', '')
    usuarios = Usuario.objects.all()

    # Aplicar filtro de búsqueda
    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) | Q(email__icontains=query) |
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

    # Aplicar filtro de rol
    if rol_filtro:
        usuarios = usuarios.filter(rol=rol_filtro)

    # Aplicar filtro de estado (usando is_active)
    if estado_filtro == 'activo':
        usuarios = usuarios.filter(is_active=True)
    elif estado_filtro == 'inactivo':
        usuarios = usuarios.filter(is_active=False)
    usuarios = usuarios.order_by('username')

    # --- Lógica de Formulario Agregar ---
    # Se maneja el POST aquí para agregar nuevos usuarios
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario "{user.username}" creado correctamente.')
            return redirect('modulo_usuarios')
        else:
             messages.error(request, 'Error al crear el usuario. Revisa el formulario.')
    else:
        form = UsuarioCreationForm()

    context = {
        'usuarios': usuarios,
        'form': form,
        'ROL_CHOICES': ROL_CHOICES,
        'edit_mode': False
    }

    # --- Respuesta Diferenciada (Normal vs AJAX) ---
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Si es AJAX (desde el filtro), renderiza SOLO la tabla parcial
        html = render_to_string(
            template_name="_user_list_partial.html", # Plantilla solo con el bucle y <tr>
            context={'usuarios': usuarios, 'request': request} # Pasar request si se usa en el parcial
        )
        # Devolver el HTML como parte de una respuesta JSON
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)
    else:
        # Si es una petición normal (GET o POST con error), renderiza la página completa
        # Asegúrate de que el nombre del template sea el correcto
        return render(request, 'modulo_usuarios.html', context)

@login_required # Proteger la vista
def editar_usuario(request, user_id):
    """
    Maneja la edición de un usuario existente. Renderiza la misma plantilla.
    """
    usuario_a_editar = get_object_or_404(Usuario, id=user_id)

    if request.method == 'POST':
        # Usar UsuarioChangeForm para editar
        form = UsuarioChangeForm(request.POST, instance=usuario_a_editar)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario "{usuario_a_editar.username}" actualizado correctamente.')
            return redirect('modulo_usuarios')
        else:
            messages.error(request, 'Error al actualizar el usuario. Revisa el formulario.')
            # Si hay error, el 'form' con errores se pasará al contexto abajo
    else:
        # Si es GET, muestra el formulario con los datos del usuario
        form = UsuarioChangeForm(instance=usuario_a_editar)

    # Siempre necesitamos la lista completa de usuarios para la tabla
    todos_los_usuarios = Usuario.objects.all().order_by('username')

    context = {
        'form': form, # Formulario (relleno con datos o con errores)
        'usuario_editado': usuario_a_editar, # El usuario específico que se está editando
        'edit_mode': True, # Bandera para la plantilla
        'usuarios': todos_los_usuarios, # Lista completa para la tabla
        'ROL_CHOICES': ROL_CHOICES # Necesario si el form se muestra en la misma página
    }
    # Renderizar la MISMA plantilla que modulo_usuarios
    return render(request, 'modulo_usuarios.html', context)


@login_required
def eliminar_usuario(request, user_id):
    """
    Elimina un usuario específico. Requiere método POST.
    """
    # Evitar que un usuario se elimine a sí mismo
    if request.user.id == user_id:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
        return redirect('modulo_usuarios')

    usuario_a_eliminar = get_object_or_404(Usuario, id=user_id)

    if request.method == 'POST':
        username_eliminado = usuario_a_eliminar.username
        usuario_a_eliminar.delete()
        messages.success(request, f'Usuario "{username_eliminado}" eliminado correctamente.')
        return redirect('modulo_usuarios')
    else:
        messages.warning(request, "La acción de eliminar debe hacerse mediante POST.")
        return redirect('modulo_usuarios')
