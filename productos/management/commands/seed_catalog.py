from django.core.management.base import BaseCommand
from productos.models import Categoria, Producto
import random
import string

class Command(BaseCommand):
    help = "Carga 1000 productos de ejemplo y sus categorías (sin Faker)."

    def handle(self, *args, **kwargs):
        self.stdout.write("🧹 Eliminando datos antiguos...")
        Producto.objects.all().delete()
        Categoria.objects.all().delete()

        categorias_nombres = ["Chocolates", "Gomitas", "Bebidas", "Galletas", "Snacks Salados"]
        categorias = {}
        for nombre in categorias_nombres:
            cat = Categoria.objects.create(nombre=nombre)
            categorias[nombre] = cat
            self.stdout.write(f"✅ Categoría creada: {nombre}")

        # === Productos base ===
        productos_base = [
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
                "marca": "Sureño Chocolates"
            },
            {
                "sku": "GO-001",
                "nombre": "Gomitas de Osito Frutales 1kg",
                "categoria": "Gomitas",
                "descripcion": "Gomitas con forma de oso y sabores frutales surtidos.",
                "precio_venta": 1500.00,
                "costo_estandar": 600.00,
                "impuesto_iva": 19.00,
                "stock_actual": 100,
                "stock_minimo": 20,
                "marca": "Frutix"
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
                "marca": "Cola Cola"
            },
        ]

        for p in productos_base:
            Producto.objects.create(
                sku=p["sku"],
                nombre=p["nombre"],
                categoria=categorias[p["categoria"]],
                descripcion=p["descripcion"],
                precio_venta=p["precio_venta"],
                costo_estandar=p["costo_estandar"],
                impuesto_iva=p["impuesto_iva"],
                stock_actual=p["stock_actual"],
                stock_minimo=p["stock_minimo"],
                marca=p.get("marca", "")
            )

        self.stdout.write("📦 Productos base creados correctamente.")

        # === Productos aleatorios ===
        total = 1000
        self.stdout.write(f"⚙️ Generando {total} productos de ejemplo adicionales...")

        palabras = [
            "Dulce", "Mix", "Extra", "Clásico", "Premium", "Natural",
            "Cremoso", "Crocante", "Ligero", "Delicia", "Especial", "Energético"
        ]

        marcas = ["Dulcix", "Snacky", "SabroMax", "ChocoBoom", "MegaSweet", "Frutix", "GalleMix"]

        categorias_keys = list(categorias.keys())
        productos_bulk = []

        for i in range(1, total + 1):
            cat_name = random.choice(categorias_keys)
            cat_obj = categorias[cat_name]

            # SKU único
            prefix = cat_name[:2].upper()
            sku = f"{prefix}-{1000 + i}"

            # Nombre y descripción
            nombre = f"{random.choice(palabras)} {cat_name[:-1]} {i}"
            descripcion = f"{nombre} con sabor irresistible y presentación de alta calidad."

            marca = random.choice(marcas)
            precio_venta = round(random.uniform(500, 6000), 2)
            costo_estandar = round(precio_venta * random.uniform(0.4, 0.8), 2)
            stock_actual = random.randint(5, 200)
            stock_minimo = random.randint(5, 30)
            iva = random.choice([19.0, 0.0])
            perishable = random.choice([True, False])

            producto = Producto(
                sku=sku,
                nombre=nombre,
                categoria=cat_obj,
                descripcion=descripcion,
                precio_venta=precio_venta,
                costo_estandar=costo_estandar,
                impuesto_iva=iva,
                stock_actual=stock_actual,
                stock_minimo=stock_minimo,
                marca=marca,
                perishable=perishable,
            )

            productos_bulk.append(producto)

            # Guardar en lotes de 200 para no saturar memoria
            if i % 200 == 0:
                Producto.objects.bulk_create(productos_bulk)
                productos_bulk.clear()
                self.stdout.write(f"  > {i} productos generados...")

        if productos_bulk:
            Producto.objects.bulk_create(productos_bulk)

        self.stdout.write(self.style.SUCCESS("🎉 ¡1000 productos creados correctamente!"))
