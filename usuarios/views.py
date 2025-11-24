import string
import secrets
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages
from django.db import IntegrityError, models
from django.utils import timezone
# IMPORTS DE SEGURIDAD
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.models import User
from .form import CustomLoginForm, UsuarioCreationForm, UsuarioChangeForm, UsuarioPerfilForm, CustomPasswordChangeForm, AvatarForm
from .models import Usuario, ROL_CHOICES 
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
import openpyxl
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from django.contrib.auth import get_backends

# --- 🔒 FILTRO DE SEGURIDAD (SOLO ADMIN) ---
def solo_admin(user):
    """Retorna True solo si el usuario es Admin o Superusuario."""
    return user.is_authenticated and (user.rol == 'admin' or user.is_superuser)

# --- HELPER: Generar Password ---
def generar_password_robusta():
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(10))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= 1):
            return password

def home(request):
    return render(request, 'home.html')

# --- REGISTRO (Protegido: Solo admin crea usuarios) ---
@login_required
@user_passes_test(solo_admin, login_url='sin_permiso')
def registrarse(request):
    if request.method == 'GET':
        form = UsuarioCreationForm()
    else:
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            pwd = generar_password_robusta()
            user.set_password(pwd)
            user.save()
            
            # Opcional: Loguear automáticamente o no.
            # Como es Admin creando otro usuario, NO logueamos al nuevo.
            # backend = get_backends()[0]
            # login(request, user, backend=backend.__class__.__name__)
            
            # Mensaje de éxito SIN contraseña en pantalla
            messages.success(request, f'Usuario "{user.username}" creado exitosamente. Se ha enviado un correo con las credenciales.')
            
            # Evidencia en consola
            print("="*60)
            print(f" [EVIDENCIA] USUARIO CREADO: {user.username}")
            print(f" [EVIDENCIA] CLAVE TEMPORAL: {pwd}")
            print("="*60)

            return redirect('modulo_usuarios')
        else:
             messages.error(request, 'Error en el registro. Revisa los datos.')
    return render(request, 'usuarios/registrarse.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('home')

def iniciar_sesion(request):
    if request.method == 'GET':
        form = CustomLoginForm(request=request)
        return render(request, 'usuarios/iniciar_sesion.html', {'form': form})
    else:
        form = CustomLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Limpieza de mensajes antiguos
            storage = messages.get_messages(request)
            for _ in storage: pass

            # Validación de Primer Login
            if getattr(user, 'must_change_password', False):
                login(request, user)
                messages.warning(request, "Por motivos de seguridad, debes cambiar tu contraseña temporal antes de continuar.")
                return redirect('cambiar_password_dedicado')

            login(request, user)
            request.session.cycle_key()
            messages.success(request, f'Bienvenido de nuevo, {user.username}.')
            return redirect('home')
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, 'usuarios/iniciar_sesion.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'iniciar_sesion.html'
    authentication_form = CustomLoginForm

class RecuperarContrasenaView(PasswordResetView):
    template_name = 'usuarios/recuperar_contrasena.html'
    email_template_name = 'usuarios/email/password_reset_email.txt'
    subject_template_name = 'usuarios/email/password_reset_subject.txt'
    success_url = reverse_lazy('iniciar_sesion')

def crear_nueva_contrasena(request):
    return render(request, 'usuarios/crear_nueva_contrasena.html')

# --- 🛡️ ZONA BLINDADA: GESTIÓN DE USUARIOS ---

@login_required
@user_passes_test(solo_admin, login_url='sin_permiso') # 🔒 CANDADO PUESTO
def modulo_usuarios(request):
    # Filtros
    query = request.GET.get('q', '')
    rol_filtro = request.GET.get('rol_filtro', '')
    estado_filtro = request.GET.get('estado_filtro', '')
    sort_by = request.GET.get('sort_by', '') 
    per_page = int(request.GET.get('per_page', 5)) 
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
    
    # Ordenamiento
    sort_mapping = {
        'username_asc': 'username', 'username_desc': '-username',
        'email_asc': 'email', 'email_desc': '-email',
        'rol_asc': 'rol', 'rol_desc': '-rol',
        'is_active_desc': '-is_active', 'is_active_asc': 'is_active',   
        'date_joined_desc': '-date_joined', 'date_joined_asc': 'date_joined',   
    }
    order_field = sort_mapping.get(sort_by, 'username') 
    usuarios = usuarios.order_by(order_field)

    # Creación de usuario (POST)
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            
            clave_temporal = generar_password_robusta()
            usuario.set_password(clave_temporal)
            usuario.must_change_password = True 
            usuario.save()
            
            # Evidencia
            print("="*60)
            print(f" [EVIDENCIA] USUARIO CREADO: {usuario.username}")
            print(f" [EVIDENCIA] CLAVE TEMPORAL: {clave_temporal}")
            print("="*60)
            
            messages.success(request, f'Usuario "{usuario.username}" creado exitosamente. Credenciales enviadas.')
            return redirect('modulo_usuarios')
        else:
            messages.error(request, 'Error al crear el usuario. Revisa el formulario.')
    else:
        form = UsuarioCreationForm()

    # Paginación
    paginator = Paginator(usuarios, per_page) 
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    params = request.GET.copy()
    params.pop('page', None)
    querystring = params.urlencode()

    context = {
        'usuarios': page_obj, 
        'page_obj': page_obj,
        'querystring': querystring,
        'form': form,
        'ROL_CHOICES': ROL_CHOICES,
        'edit_mode': False,
        'per_page': per_page, 
        'sort_by': sort_by,   
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        table_html = render_to_string("usuarios/_user_list_partial.html", context, request=request)
        pagination = render_to_string("usuarios/_user_pagination.html", context, request=request)
        return JsonResponse({"html_from_view": table_html, "pagination_html": pagination})
    else:
        return render(request, 'usuarios/modulo_usuarios.html', context)

@login_required 
@user_passes_test(solo_admin, login_url='sin_permiso') # 🔒 CANDADO PUESTO
def editar_usuario(request, user_id):
    usuario_a_editar = get_object_or_404(Usuario, id=user_id)

    if request.method == 'POST':
        form = UsuarioChangeForm(request.POST, instance=usuario_a_editar)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario "{usuario_a_editar.username}" actualizado correctamente.')
            return redirect('modulo_usuarios')
        else:
            messages.error(request, 'Error al actualizar el usuario. Revisa el formulario.')
    else:
        form = UsuarioChangeForm(instance=usuario_a_editar)

    todos_los_usuarios = Usuario.objects.all().order_by('username')
    context = {
        'form': form, 'usuario_editado': usuario_a_editar, 
        'edit_mode': True, 'usuarios': todos_los_usuarios, 'ROL_CHOICES': ROL_CHOICES 
    }
    return render(request, 'usuarios/modulo_usuarios.html', context)

@login_required
@user_passes_test(solo_admin, login_url='sin_permiso') # 🔒 CANDADO PUESTO
def eliminar_usuario(request, user_id):
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
@user_passes_test(solo_admin, login_url='sin_permiso') # 🔒 CANDADO PUESTO
def exportar_excel_usuarios(request):
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

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Usuarios"
    ws.append(["ID", "Username", "Email", "Nombre", "Apellido", "Rol", "Estado", "Último Acceso"])

    for usuario in usuarios:
        ws.append([
            usuario.id, usuario.username, usuario.email, usuario.first_name, usuario.last_name,
            usuario.get_rol_display(), "Activo" if usuario.is_active else "Inactivo",
            usuario.last_login.strftime('%Y-%m-%d %H:%M:%S') if usuario.last_login else "Nunca"
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lista_usuarios.xlsx'
    wb.save(response)
    return response

# --- VISTA DEDICADA CAMBIO PASSWORD ---
@login_required
def cambiar_password_dedicado(request):
    """
    Vista exclusiva para cambiar contraseña.
    Se usa tanto para el cambio voluntario como para el cambio forzado.
    """
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Apagar flag
            if hasattr(user, 'must_change_password') and user.must_change_password:
                user.must_change_password = False
                user.save()
            
            update_session_auth_hash(request, user)
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect('home')
        else:
            messages.error(request, "Por favor corrige los errores abajo.")
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'usuarios/cambiar_password.html', {'form': form})

def sin_permiso(request):
    return render(request, 'usuarios/sin_permiso.html')