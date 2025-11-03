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
                "stock_actual": 50,
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
                "stock_actual": 100,
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
                "stock_actual": 80,
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
                "stock_actual": 30,
                "stock_minimo": 15,
                "control_por_lote": True,
                "perishable": True
            },
            {
                "sku": "SN-001",
                "nombre": "Papas Fritas Onduladas Sabor Queso",
                "categoria": "Snacks Salados",
                "descripcion": "Crujientes papas fritas onduladas con un intenso sabor a queso.",
                "precio_venta": 950.00,
                "costo_estandar": 400.00,
                "impuesto_iva": 19.00,
                "stock_actual": 60,
                "stock_minimo": 30,
                "marca": "Snacky"
            },
            {
                "sku": "BE-002",
                "nombre": "Jugo de Naranja Natural 1L",
                "categoria": "Bebidas",
                "descripcion": "Jugo 100% natural de naranja exprimida, sin azúcar añadida.",
                "precio_venta": 1800.00,
                "costo_estandar": 850.00,
                "impuesto_iva": 19.00,
                "stock_actual": 40,
                "stock_minimo": 12,
                "perishable": True,
                "marca": "Frutix"
            },
            {
                "sku": "CH-002",
                "nombre": "Tableta de Chocolate Blanco Cremoso",
                "categoria": "Chocolates",
                "descripcion": "Suave y cremoso chocolate blanco, perfecto para disfrutar solo o en postres.",
                "precio_venta": 2200.00,
                "costo_estandar": 1100.00,
                "impuesto_iva": 19.00,
                "stock_actual": 25,
                "stock_minimo": 15,
                "marca": "Sureño Chocolates"
            },
            {
                "sku": "GO-002",
                "nombre": "Gomitas Ácidas de Tiras",
                "categoria": "Gomitas",
                "descripcion": "Tiras de gomita con cobertura ácida, sabor a tutti frutti.",
                "precio_venta": 1200.00,
                "costo_estandar": 500.00,
                "impuesto_iva": 19.00,
                "stock_actual": 150,
                "stock_minimo": 25,
                "perishable": False
            },
            {
                "sku": "GA-002",
                "nombre": "Galletas con Chips de Chocolate",
                "categoria": "Galletas",
                "descripcion": "Clásicas galletas crujientes con abundantes chips de chocolate.",
                "precio_venta": 1500.00,
                "costo_estandar": 700.00,
                "impuesto_iva": 19.00,
                "stock_actual": 70,
                "stock_minimo": 20,
                "marca": "Galletitas"
            },
            {
                "sku": "SN-002",
                "nombre": "Maní Salado Tostado 200g",
                "categoria": "Snacks Salados",
                "descripcion": "Maní seleccionado, tostado y con el punto justo de sal.",
                "precio_venta": 1300.00,
                "costo_estandar": 550.00,
                "impuesto_iva": 19.00,
                "stock_actual": 90,
                "stock_minimo": 40,
                "marca": "Snacky"
            },
            {
                "sku": "BE-003",
                "nombre": "Agua Mineral sin Gas 600ml",
                "categoria": "Bebidas",
                "descripcion": "Agua mineral de vertiente, pura y refrescante.",
                "precio_venta": 600.00,
                "costo_estandar": 250.00,
                "impuesto_iva": 19.00,
                "stock_actual": 200,
                "stock_minimo": 50,
                "marca": "Aquapura"
            },
            {
                "sku": "CH-003",
                "nombre": "Caja de Bombones Surtidos 12 Un.",
                "categoria": "Chocolates",
                "descripcion": "Elegante caja con 12 bombones de distintos rellenos: manjar, trufa y avellana.",
                "precio_venta": 5500.00,
                "costo_estandar": 2800.00,
                "impuesto_iva": 19.00,
                "stock_actual": 15,
                "stock_minimo": 8,
                "perishable": True,
                "marca": "Sureño Chocolates"
            },
            {
                "sku": "GO-003",
                "nombre": "Bolsa de Marshmallows Clásicos",
                "categoria": "Gomitas",
                "descripcion": "Suaves y esponjosos marshmallows, ideales para fogatas o chocolate caliente.",
                "precio_venta": 1800.00,
                "costo_estandar": 800.00,
                "impuesto_iva": 19.00,
                "stock_actual": 50,
                "stock_minimo": 15
            },
            {
                "sku": "SN-003",
                "nombre": "Palomitas de Maíz para Microondas",
                "categoria": "Snacks Salados",
                "descripcion": "Bolsa de palomitas de maíz sabor mantequilla, listas en 3 minutos.",
                "precio_venta": 750.00,
                "costo_estandar": 300.00,
                "impuesto_iva": 19.00,
                "stock_actual": 40,
                "stock_minimo": 25
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