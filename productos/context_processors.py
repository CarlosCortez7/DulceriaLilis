def cart_item_count(request):
    """
    Calcula el número total de artículos en el carrito de compras
    y lo hace disponible en el contexto de todas las plantillas.
    """
    carrito = request.session.get('carrito', {})
    count = sum(carrito.values())
    return {'cart_item_count': count}
