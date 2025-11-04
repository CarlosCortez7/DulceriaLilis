from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.forms import UserCreationForm
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

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise forms.ValidationError('El nombre de usuario debe tener al menos 3 caracteres.')
        return username
    
class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'telefono', 'rol', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Usuario'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Correo electrónico'})
        self.fields['telefono'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Teléfono'})
        self.fields['rol'].widget.attrs.update({'class': 'form-select'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Repetir Contraseña'})
        self.fields['rol'].choices = [choice for choice in self.fields['rol'].choices if choice[0] != 'admin' or choice[0] == 'Administrador']

class UsuarioChangeForm(UserChangeForm):
    # Quitar el campo password para que no se muestre/edite aquí
    password = None

    class Meta:
        model = Usuario
        # Incluir los campos que quieres permitir editar
        # Usamos los campos de AbstractUser + los tuyos propios
        fields = ['username', 'email', 'first_name', 'last_name',
                  'telefono', 'rol', 'is_active', # Usar is_active en lugar de 'estado'
                  'mfa_habilitado', 'observaciones', 'area_unidad',
                  'is_staff', 'is_superuser', 'groups', 'user_permissions'] # Campos estándar de permisos

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # (Opcional) Añadir clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                 field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Select):
                 field.widget.attrs.update({'class': 'form-select'})
            elif not isinstance(field.widget, forms.SelectMultiple): # Evitar aplicar a permisos/grupos
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
            raise forms.ValidationError("Solo JPG o PNG.")
        if avatar.size > 2 * 1024 * 1024:  # 2 MB
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