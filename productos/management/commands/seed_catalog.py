from django.core.management.base import BaseCommand
from productos.models import Categoria, Producto

class Command(BaseCommand):
    help = "Carga semillas de catálogo inicial"

    def handle(self, *args, **kwargs):
        # Crear categorías
        categorias = ["Dulces", "Bebidas"]
        for cat in categorias:
            Categoria.objects.get_or_create(nombre=cat)

        # Crear productos
        productos = [
            {"id_interno": "10452", "nombre": "Chocolate Amargo Sureño", "categoria": "Dulces", "stock_actual": 10, "estado": "activo"},
            {"id_interno": "10453", "nombre": "Chocolate con Leche", "categoria": "Dulces", "stock_actual": 15, "estado": "activo"},
            {"id_interno": "10454", "nombre": "Bebida Cola Cola", "categoria": "Bebidas", "stock_actual": 20, "estado": "activo"},
        ]

        for p in productos:
            cat_obj = Categoria.objects.get(nombre=p["categoria"])
            Producto.objects.update_or_create(
                id_interno=p["id_interno"],
                defaults={
                    "nombre": p["nombre"],
                    "categoria": cat_obj,
                    "stock_actual": p["stock_actual"],
                    "estado": p["estado"]
                }
            )

        self.stdout.write(self.style.SUCCESS("Semillas cargadas correctamente"))
