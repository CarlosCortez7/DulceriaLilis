from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Datos adicionales', {
            'fields': ('telefono', 'rol', 'mfa_habilitado', 'observaciones', 'area_unidad')
        }),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active', 'last_login')
    list_filter = ('rol', 'is_active', 'mfa_habilitado', 'is_staff', 'is_superuser')