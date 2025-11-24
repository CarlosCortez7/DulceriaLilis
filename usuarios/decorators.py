from django.contrib.auth.decorators import user_passes_test

def solo_inventario(user):
    """Permite acceso solo a usuarios con rol 'inventario' o 'admin'"""
    return user.is_authenticated and (user.rol == 'inventario' or user.rol == 'admin' or user.is_superuser or user.rol == 'finanzas')

def solo_compras(user):
    return user.is_authenticated and (user.rol == 'compras' or user.rol == 'admin')

def solo_produccion(user):
    return user.is_authenticated and (user.rol == 'produccion' or user.rol == 'admin')

def solo_ventas(user):
    return user.is_authenticated and (user.rol == 'ventas' or user.rol == 'admin')
