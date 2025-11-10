from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth import authenticate
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
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Intentar autenticar primero como si fuera un correo
            try:
                user_obj = Usuario.objects.get(email__iexact=username)
                username = user_obj.username  # reemplazamos por el username real
            except Usuario.DoesNotExist:
                pass  # si no existe por email, intenta con username normal

            user = authenticate(self.request, username=username, password=password)

            if user is None:
                raise forms.ValidationError("Correo o contraseña incorrectos.")
            if not user.is_active:
                raise forms.ValidationError("Esta cuenta está desactivada.")
        else:
            raise forms.ValidationError("Debes ingresar tus credenciales.")

        self.user_cache = user
        return self.cleaned_data


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
    password = None  # No mostrar ni editar la contraseña aquí

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
