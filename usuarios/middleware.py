from django.shortcuts import redirect
from django.urls import reverse

class ForcePasswordChangeMiddleware:
    """
    Middleware que obliga al usuario a cambiar su contraseña si el flag
    'must_change_password' está activo. Bloquea la navegación a cualquier
    otra página excepto el cambio de clave y el logout.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Verificamos si el usuario está logueado y tiene el bloqueo activo
        if request.user.is_authenticated and getattr(request.user, 'must_change_password', False):
            
            # 2. Definimos las únicas rutas permitidas (Lista Blanca)
            # Es vital permitir 'logout' por si se arrepiente y quiere salir.
            rutas_permitidas = [
                reverse('cambiar_password_dedicado'),
                reverse('logout'), 
            ]
            
            # 3. Si intenta ir a cualquier ruta que NO esté en la lista permitida...
            if request.path not in rutas_permitidas:
                # ... ¡Lo mandamos de vuelta a cambiar la contraseña!
                return redirect('cambiar_password_dedicado')

        response = self.get_response(request)
        return response