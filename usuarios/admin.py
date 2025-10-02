from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario
from .models import Tareas

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Datos adicionales', {
            'fields': ('telefono', 'rol', 'estado', 'ultimo_acceso', 'mfa_habilitado', 'observaciones')
        }),
    )
    list_display = ('username', 'email', 'rol', 'estado', 'ultimo_acceso')
    list_filter = ('rol', 'estado', 'mfa_habilitado')

class TareaAdmin(admin.ModelAdmin):
    readonly_fields = ("fecha_creacion", )

admin.site.register(Tareas, TareaAdmin)