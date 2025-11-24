from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth import authenticate
# --- IMPORTACIONES FALTANTES PARA EL BLOQUEO ---
from django.utils import timezone
from datetime import timedelta
from .models import Usuario

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Correo o nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu usuario o correo'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña'
        })
    )

    def clean(self):
        username_input = self.cleaned_data.get('username')
        password_input = self.cleaned_data.get('password')

        if username_input and password_input:
            # 1. Buscar al usuario para verificar si existe y si está bloqueado
            user_obj = None
            try:
                user_obj = Usuario.objects.get(email__iexact=username_input)
            except Usuario.DoesNotExist:
                try:
                    user_obj = Usuario.objects.get(username__iexact=username_input)
                except Usuario.DoesNotExist:
                    # Si no existe, dejamos que authenticate falle después, 
                    # pero no podemos bloquear a alguien que no existe.
                    pass

            # 2. VERIFICAR SI ESTÁ BLOQUEADO (Antes de validar contraseña)
            if user_obj and user_obj.bloqueado_hasta and user_obj.bloqueado_hasta > timezone.now():
                tiempo_restante = int((user_obj.bloqueado_hasta - timezone.now()).total_seconds() / 60) + 1
                raise forms.ValidationError(f"Cuenta bloqueada por seguridad. Inténtalo de nuevo en {tiempo_restante} minutos.")

            # 3. INTENTAR AUTENTICAR
            # Usamos el username real del objeto si lo encontramos, si no, el input original
            auth_username = user_obj.username if user_obj else username_input
            user = authenticate(self.request, username=auth_username, password=password_input)

            if user is None:
                # --- PASSWORD INCORRECTA: LÓGICA DE BLOQUEO ---
                if user_obj:
                    user_obj.intentos_fallidos += 1
                    
                    # Límite de 5 intentos
                    if user_obj.intentos_fallidos >= 5:
                        user_obj.bloqueado_hasta = timezone.now() + timedelta(minutes=3)
                        user_obj.intentos_fallidos = 0 # Reiniciamos para el siguiente ciclo
                        user_obj.save()
                        raise forms.ValidationError("Has excedido los 5 intentos. Tu cuenta ha sido bloqueada por 3 minutos.")
                    
                    user_obj.save()
                    restantes = 5 - user_obj.intentos_fallidos
                    raise forms.ValidationError(f"Contraseña incorrecta. Te quedan {restantes} intentos antes del bloqueo.")
                
                raise forms.ValidationError("Correo o contraseña incorrectos.")

            else:
                # --- LOGIN EXITOSO: RESETEAR CONTADORES ---
                # Si el login es correcto, limpiamos cualquier intento fallido previo
                if user_obj:
                    user_obj.intentos_fallidos = 0
                    user_obj.bloqueado_hasta = None
                    user_obj.save()

                if not user.is_active:
                    raise forms.ValidationError("Esta cuenta está desactivada.")
                
                self.user_cache = user
        else:
            raise forms.ValidationError("Debes ingresar tus credenciales.")

        return self.cleaned_data


class UsuarioCreationForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'telefono', 'rol']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Usuario'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Correo electrónico'})
        self.fields['telefono'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Teléfono'})
        self.fields['rol'].widget.attrs.update({'class': 'form-select'})
        
        if 'rol' in self.fields:
            self.fields['rol'].choices = [choice for choice in self.fields['rol'].choices if choice[0] != 'admin' or choice[0] == 'Administrador']


class UsuarioChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'telefono', 'rol', 'is_active',
            'mfa_habilitado', 'observaciones', 'area_unidad',
            'is_staff', 'is_superuser', 'groups', 'user_permissions'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif not isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs.update({'class': 'form-control'})


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if not avatar:
            raise forms.ValidationError("Selecciona una imagen.")
        if avatar.content_type not in ['image/jpeg', 'image/png']:
            raise forms.ValidationError("Solo se permiten imágenes JPG o PNG.")
        if avatar.size > 2 * 1024 * 1024:
            raise forms.ValidationError("La imagen no debe superar los 2MB.")
        return avatar


class UsuarioPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. +56912345678'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña actual'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'}),
        help_text="Debe tener al menos 8 caracteres, una mayúscula y un número."
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar nueva contraseña'})
    )

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise forms.ValidationError("Debe tener al menos 8 caracteres.")
        if not any(c.isupper() for c in password):
            raise forms.ValidationError("Debe contener al menos una mayúscula.")
        if not any(c.isdigit() for c in password):
            raise forms.ValidationError("Debe contener al menos un número.")
        return password