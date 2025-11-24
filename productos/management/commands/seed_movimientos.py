from django.core.management.base import BaseCommand
from django.utils import timezone
from productos.models import MovimientoInventario, Producto
from usuarios.models import Usuario  # ajusta si tu modelo está en otro lugar
import random
import datetime
import string


class Command(BaseCommand):
    help = "Genera 10.000 movimientos de inventario para pruebas."

    def handle(self, *args, **kwargs):
        self.stdout.write("➡ Cargando productos y usuarios...")

        productos = list(Producto.objects.all())
        usuarios = list(Usuario.objects.all())

        if not productos:
            self.stdout.write(self.style.ERROR("❌ No hay productos en la BD."))
            return

        if not usuarios:
            self.stdout.write(self.style.ERROR("❌ No hay usuarios en la BD."))
            return

        self.stdout.write(self.style.SUCCESS("✔ Productos y usuarios cargados."))

        self.stdout.write("➡ Generando movimientos...")

        movimientos = []

        for i in range(10000):
            producto = random.choice(productos)
            usuario = random.choice(usuarios)

            tipo = random.choice(["INGRESO", "SALIDA"])
            cantidad = random.randint(1, 120)

            if tipo == "SALIDA" and producto.stock_actual < cantidad:
                cantidad = max(1, producto.stock_actual)

            # Fechas aleatorias en los últimos 120 días
            fecha = timezone.now() - datetime.timedelta(days=random.randint(0, 120))

            movimiento = MovimientoInventario(
                producto=producto,
                usuario=usuario,
                tipo_movimiento=tipo,
                cantidad=cantidad,
                fecha_movimiento=fecha,
                documento_referencia=f"DOC-{random.randint(1000, 9999)}",
                lote=f"L-{random.randint(1000, 9999)}" if random.choice([True, False]) else None,
                serie=''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                       if random.choice([True, False]) else None,
                fecha_vencimiento=fecha + datetime.timedelta(days=random.randint(30, 365))
                                    if random.choice([True, False]) else None,
            )

            movimientos.append(movimiento)

            # Actualizar stock
            if tipo == "INGRESO":
                producto.stock_actual += cantidad
            else:
                producto.stock_actual = max(0, producto.stock_actual - cantidad)

            # Guardar cada cierto número para no reventar memoria
            if i % 500 == 0:
                Producto.objects.bulk_update(productos, ['stock_actual'])
                MovimientoInventario.objects.bulk_create(movimientos)
                movimientos = []
                self.stdout.write(f"  → {i} movimientos generados...")

        # Guardar lo que faltaba
        Producto.objects.bulk_update(productos, ['stock_actual'])
        MovimientoInventario.objects.bulk_create(movimientos)

        self.stdout.write(self.style.SUCCESS("✔ Se generaron 10.000 movimientos correctamente."))

