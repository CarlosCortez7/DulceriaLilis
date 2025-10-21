from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .models import Proveedor  # ¡Importante! Asegúrate de tener este modelo
import openpyxl  # Necesitarás instalar esto: pip install openpyxl

# --- Vistas Principales del Módulo ---

def modulo_proveedores(request):
    """
    Muestra la lista de proveedores y el formulario de creación.
    También maneja la búsqueda (filtro GET).
    """
    query = request.GET.get('q')
    if query:
        # Búsqueda por RUT/NIF o Razón Social
        proveedores = Proveedor.objects.filter(
            Q(rut_nif__icontains=query) | Q(razon_social__icontains=query)
        ).order_by('razon_social')
    else:
        proveedores = Proveedor.objects.all().order_by('razon_social')

    context = {
        'titulo_pagina': 'Módulo de Proveedores',
        'proveedores': proveedores,
        # 'proveedor_a_editar' se usa para pre-llenar el formulario en modo edición
    }
    return render(request, 'proveedores/lista.html', context)

def guardar_proveedor(request):
    """
    Procesa el formulario para CREAR un nuevo proveedor.
    """
    if request.method == 'POST':
        try:
            # Recupera todos los campos del formulario
            rut_nif = request.POST.get('rut_nif')
            
            # Verificación simple para evitar duplicados
            if Proveedor.objects.filter(rut_nif=rut_nif).exists():
                messages.error(request, f'Error: El RUT/NIF {rut_nif} ya existe.')
                return redirect('modulo_proveedores')

            Proveedor.objects.create(
                rut_nif=request.POST.get('rut_nif'),
                razon_social=request.POST.get('razon_social'),
                nombre_fantasia=request.POST.get('nombre_fantasia'),
                email=request.POST.get('email'),
                telefono=request.POST.get('telefono'),
                sitio_web=request.POST.get('sitio_web'),
                direccion_fisica=request.POST.get('direccion_fisica'),
                comuna=request.POST.get('comuna'),
                ciudad=request.POST.get('ciudad'),
                region=request.POST.get('region'),
                contacto_comercial=request.POST.get('contacto_comercial'),
                telefono_comercial=request.POST.get('telefono_comercial'),
                dias_credito=request.POST.get('dias_credito', 0),
                estado=request.POST.get('estado')
            )
            messages.success(request, 'Proveedor guardado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al guardar el proveedor: {e}')
            
    return redirect('modulo_proveedores')

# --- MÓDULOS FALTANTES AQUÍ ---

def editar_proveedor(request, proveedor_id):
    """
    Maneja tanto la carga del formulario de EDICIÓN (GET) 
    como la actualización del proveedor (POST).
    """
    proveedor_a_editar = get_object_or_404(Proveedor, id=proveedor_id)

    if request.method == 'POST':
        # --- Lógica de Actualización (POST) ---
        try:
            proveedor_a_editar.rut_nif = request.POST.get('rut_nif')
            proveedor_a_editar.razon_social = request.POST.get('razon_social')
            proveedor_a_editar.nombre_fantasia = request.POST.get('nombre_fantasia')
            proveedor_a_editar.email = request.POST.get('email')
            proveedor_a_editar.telefono = request.POST.get('telefono')
            proveedor_a_editar.sitio_web = request.POST.get('sitio_web')
            proveedor_a_editar.direccion_fisica = request.POST.get('direccion_fisica')
            proveedor_a_editar.comuna = request.POST.get('comuna')
            proveedor_a_editar.ciudad = request.POST.get('ciudad')
            proveedor_a_editar.region = request.POST.get('region')
            proveedor_a_editar.contacto_comercial = request.POST.get('contacto_comercial')
            proveedor_a_editar.telefono_comercial = request.POST.get('telefono_comercial')
            proveedor_a_editar.dias_credito = request.POST.get('dias_credito', 0)
            proveedor_a_editar.estado = request.POST.get('estado')
            
            proveedor_a_editar.save()
            messages.success(request, 'Proveedor actualizado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al actualizar el proveedor: {e}')
        
        return redirect('modulo_proveedores')

    else:
        # --- Lógica para Cargar Datos (GET) ---
        # Renderiza la misma plantilla, pero con los datos del proveedor
        # para que el formulario se llene automáticamente.
        proveedores = Proveedor.objects.all().order_by('razon_social')
        context = {
            'titulo_pagina': 'Editar Proveedor',
            'proveedores': proveedores,
            'proveedor_a_editar': proveedor_a_editar  # Clave para rellenar el formulario
        }
        return render(request, 'proveedores/lista.html', context)

def eliminar_proveedor(request, proveedor_id):
    """
    Busca un proveedor por su ID y lo elimina.
    """
    # Usamos POST para eliminar por seguridad, pero si usas un enlace (GET)
    # puedes quitar la validación 'if request.method == 'POST':'.
    # El 'onclick' de tu plantilla ya pide confirmación, así que un GET es aceptable aquí.
    try:
        proveedor = get_object_or_404(Proveedor, id=proveedor_id)
        nombre_proveedor = proveedor.razon_social
        proveedor.delete()
        messages.success(request, f'Proveedor "{nombre_proveedor}" eliminado.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el proveedor: {e}')
        
    return redirect('modulo_proveedores')

def exportar_excel_proveedores(request):
    """
    Genera un archivo Excel con la lista de todos los proveedores.
    """
    # Validar que el usuario tenga permisos (si es necesario)
    # if not request.user.is_staff:
    #     messages.error(request, 'No tienes permisos para esta acción.')
    #     return redirect('modulo_proveedores')

    proveedores = Proveedor.objects.all()

    # Crear un nuevo libro de Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Proveedores"

    # Escribir los encabezados
    headers = [
        "ID", "RUT/NIF", "Razón Social", "Nombre Fantasía", 
        "Email", "Teléfono", "Sitio Web", "Estado", 
        "Contacto Comercial", "Teléfono Contacto"
    ]
    ws.append(headers)

    # Escribir los datos de cada proveedor
    for p in proveedores:
        ws.append([
            p.id, p.rut_nif, p.razon_social, p.nombre_fantasia,
            p.email, p.telefono, p.sitio_web, p.estado,
            p.contacto_comercial, p.telefono_comercial
        ])

    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=lista_proveedores.xlsx'
    
    # Guardar el libro de Excel en la respuesta
    wb.save(response)

    return response