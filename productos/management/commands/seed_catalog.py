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
            {
                "id_interno": "10452",
                "nombre": "Chocolate Amargo Sureño",
                "categoria": "Dulces",
                "estado": "activo",
                "unidad_medida": "unidad",
                "descripcion": "Chocolate amargo importado del sur."
            },
            {
                "id_interno": "10453",
                "nombre": "Chocolate con Leche",
                "categoria": "Dulces",
                "estado": "activo",
                "unidad_medida": "unidad",
                "descripcion": "Chocolate con leche de primera calidad."
            },
            {
                "id_interno": "10454",
                "nombre": "Bebida Cola Cola",
                "categoria": "Bebidas",
                "estado": "activo",
                "unidad_medida": "ml",
                "descripcion": "Bebida gaseosa sabor cola."
            },
        ]

        for p in productos:
            cat_obj = Categoria.objects.get(nombre=p["categoria"])
            Producto.objects.update_or_create(
                id_interno=p["id_interno"],
                defaults={
                    "nombre": p["nombre"],
                    "categoria": cat_obj,
                    "estado": p["estado"],
                    "unidad_medida": p["unidad_medida"],
                    "descripcion": p.get("descripcion", "")
                }
            )

        self.stdout.write(self.style.SUCCESS("Semillas cargadas correctamente"))
