from django.core.management.base import BaseCommand
from productos.models import Categoria, Producto

class Command(BaseCommand):
    help = "Carga el catálogo inicial de productos y categorías para la Dulcería Lilis."

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando la carga de semillas...")

        Producto.objects.all().delete()
        Categoria.objects.all().delete()
        self.stdout.write("Datos antiguos de productos y categorías eliminados.")

        categorias = ["Chocolates", "Gomitas", "Bebidas", "Galletas", "Snacks Salados"]
        cat_objects = {}
        for cat_nombre in categorias:
            cat_obj, created = Categoria.objects.get_or_create(nombre=cat_nombre)
            cat_objects[cat_nombre] = cat_obj
            if created:
                self.stdout.write(f"- Categoría '{cat_nombre}' creada.")

        productos_data = [
            {
                "sku": "CH-001",
                "nombre": "Chocolate Amargo Sureño 80%",
                "categoria": "Chocolates",
                "descripcion": "Chocolate amargo premium con 80% de cacao, ideal para repostería.",
                "precio_venta": 2500.00,
                "costo_estandar": 1200.00,
                "impuesto_iva": 19.00,
                "stock_minimo": 10,
                "perishable": True,
                "control_por_lote": True,
                "marca": "Sureño Chocolates"
            },
            {
                "sku": "GO-001",
                "nombre": "Gomitas de Osito Frutales 1kg",
                "categoria": "Gomitas",
                "descripcion": "Gomitas con forma de oso y sabores frutales surtidos, formato familiar.",
                "precio_venta": 1500.00,
                "costo_estandar": 600.00,
                "impuesto_iva": 19.00,
                "stock_minimo": 20,
                "perishable": True,
                "uom_compra": "kg",
                "uom_venta": "gramo",
                "factor_conversion": 1000,
            },
            {
                "sku": "BE-001",
                "nombre": "Bebida Cola Cola 500ml",
                "categoria": "Bebidas",
                "descripcion": "Bebida gaseosa refrescante sabor cola.",
                "precio_venta": 800.00,
                "costo_estandar": 350.00,
                "impuesto_iva": 19.00,
                "stock_minimo": 24,
                "uom_venta": "unidad",
                "marca": "Cola Cola"
            },
            {
                "sku": "GA-001",
                "nombre": "Galletas de Avena y Miel (Paquete)",
                "categoria": "Galletas",
                "descripcion": "Galletas artesanales hechas con avena integral y miel de campo.",
                "precio_venta": 2200.00,
                "costo_estandar": 900.00,
                "impuesto_iva": 19.00,
                "stock_minimo": 15,
                "control_por_lote": True,
                "perishable": True
            },
        ]

        for p_data in productos_data:
            categoria_nombre = p_data.pop("categoria")
            cat_obj = cat_objects[categoria_nombre]
            
            Producto.objects.update_or_create(
                sku=p_data["sku"],
                defaults={
                    "categoria": cat_obj,
                    **p_data
                }
            )
        
        self.stdout.write(f"- {len(productos_data)} productos creados/actualizados.")
        self.stdout.write(self.style.SUCCESS("¡Semillas cargadas correctamente!"))