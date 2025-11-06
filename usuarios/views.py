from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages
from django.db import IntegrityError, models
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from .form import CustomLoginForm, UsuarioCreationForm, UsuarioChangeForm, UsuarioPerfilForm, CustomPasswordChangeForm, AvatarForm
from .models import Usuario, ROL_CHOICES # Importar ROL_CHOICES si está definido en models.py
# Importar Q para búsquedas OR
from django.db.models import Q
# Importar para renderizar solo una parte (AJAX)
from django.template.loader import render_to_string
from django.http import JsonResponse
# Para exportar a Excel
from django.http import HttpResponse
import openpyxl
# Importar para paginación
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
            messages.success(request, f'¡Bienvenido, {user.username}! Registro exitoso.')
            return redirect('home')
        else:
             messages.error(request, 'Error en el registro. Revisa los datos.')
    return render(request, 'usuarios/registrarse.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('home')

def iniciar_sesion(request):
    if request.method == 'GET':
        form = CustomLoginForm()
        return render(request, 'usuarios/iniciar_sesion.html', {'form': form})
    else:
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session.cycle_key() # Regenerar clave de sesión por seguridad
            messages.success(request, f'Bienvenido de nuevo, {user.username}.')
            return redirect('home')
        else:
            return render(request, 'usuarios/iniciar_sesion.html', {
                'form': form,
            })

class CustomLoginView(LoginView):
    template_name = 'iniciar_sesion.html'
    authentication_form = CustomLoginForm

def recuperar_contrasenea(request):
    return render(request, 'usuarios/recuperar_contrasena.html')

def crear_nueva_contrasena(request):
    return render(request, 'usuarios/crear_nueva_contrasena.html')

@login_required
def modulo_usuarios(request):
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

    # --- Lógica de Paginación ---
    paginator = Paginator(usuarios, 5) # 5 usuarios por página
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Conservar parámetros de búsqueda en la paginación
    params = request.GET.copy()
    params.pop('page', None)
    querystring = params.urlencode()

    context = {
        'usuarios': page_obj, # Usar el objeto de página en lugar de la lista completa
        'page_obj': page_obj,
        'querystring': querystring,
        'form': form,
        'ROL_CHOICES': ROL_CHOICES,
        'edit_mode': False,
    }

    # --- Respuesta Diferenciada (Normal vs AJAX) ---
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Si es AJAX (desde el filtro), renderiza SOLO la tabla parcial
        html = render_to_string(
            template_name="usuarios/_user_list_partial.html", # Ruta correcta para la plantilla parcial
            context=context # Pasamos el contexto completo que ya tiene page_obj
        )
        # Devolver el HTML como parte de una respuesta JSON
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)
    else:
        # Si es una petición normal (GET o POST con error), renderiza la página completa
        # Asegúrate de que el nombre del template sea el correcto
        return render(request, 'usuarios/modulo_usuarios.html', context)

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
    return render(request, 'usuarios/modulo_usuarios.html', context)


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

@login_required
def exportar_excel_usuarios(request):
    """
    Genera un archivo Excel con la lista de usuarios, aplicando los filtros actuales.
    """
    # 1. Replicar la lógica de filtrado de la vista principal
    query = request.GET.get('q', '')
    rol_filtro = request.GET.get('rol_filtro', '')
    estado_filtro = request.GET.get('estado_filtro', '')
    usuarios = Usuario.objects.all()

    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) | Q(email__icontains=query) |
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
    if rol_filtro:
        usuarios = usuarios.filter(rol=rol_filtro)
    if estado_filtro == 'activo':
        usuarios = usuarios.filter(is_active=True)
    elif estado_filtro == 'inactivo':
        usuarios = usuarios.filter(is_active=False)
    
    usuarios = usuarios.order_by('username')

    # 2. Crear el libro de Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Usuarios"

    # Escribir encabezados
    headers = ["ID", "Username", "Email", "Nombre", "Apellido", "Rol", "Estado", "Último Acceso"]
    ws.append(headers)

    # Escribir datos de cada usuario
    for usuario in usuarios:
        ws.append([
            usuario.id, usuario.username, usuario.email, usuario.first_name, usuario.last_name,
            usuario.get_rol_display(), "Activo" if usuario.is_active else "Inactivo",
            usuario.last_login.strftime('%Y-%m-%d %H:%M:%S') if usuario.last_login else "Nunca"
        ])

    # 3. Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lista_usuarios.xlsx'
    wb.save(response)

    return response

@login_required
def perfil_usuario(request):
    user = request.user

    if request.method == 'POST':
        if 'actualizar_imagen' in request.POST:  # <- nombre del botón del form de imagen
            avatar_form = AvatarForm(request.POST, request.FILES, instance=user)
            perfil_form = UsuarioPerfilForm(instance=user)
            password_form = CustomPasswordChangeForm(user)
            if avatar_form.is_valid():
                avatar_form.save()
                messages.success(request, "Imagen de perfil actualizada correctamente.")
                return redirect('perfil_usuario')
            else:
                messages.error(request, "No se pudo actualizar la imagen.")
        elif 'actualizar_datos' in request.POST:
            perfil_form = UsuarioPerfilForm(request.POST, instance=user)
            avatar_form = AvatarForm(instance=user)
            password_form = CustomPasswordChangeForm(user)
            if perfil_form.is_valid():
                perfil_form.save()
                messages.success(request, "Datos personales actualizados.")
                return redirect('perfil_usuario')
            else:
                messages.error(request, "Corrige los errores del formulario.")
        elif 'cambiar_password' in request.POST:
            password_form = CustomPasswordChangeForm(user, request.POST)
            perfil_form = UsuarioPerfilForm(instance=user)
            avatar_form = AvatarForm(instance=user)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña actualizada.")
                return redirect('perfil_usuario')
            else:
                messages.error(request, "Revisa los campos de contraseña.")
    else:
        perfil_form = UsuarioPerfilForm(instance=user)
        avatar_form = AvatarForm(instance=user)
        password_form = CustomPasswordChangeForm(user)

    return render(request, 'usuarios/perfil.html', {
        'perfil_form': perfil_form,
        'avatar_form': avatar_form,
        'password_form': password_form,
    })