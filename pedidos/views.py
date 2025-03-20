from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import transaction, IntegrityError
from .models import Producto, Pedido, ItemPedido, ClienteAnonimo
from .forms import PedidoForm, ItemPedidoForm, ProductoForm, ClienteAnonimoForm
import datetime



def home(request):
    productos = Producto.objects.all()
    year = datetime.datetime.now().year
    context = {
        'productos': productos,
        'year': year,
        
    }
    return render(request, 'pedidos/home.html', context)


def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Producto agregado con éxito.")
                return redirect('listar_productos')
            except IntegrityError:
                messages.error(request, "Error al agregar el producto. Ya existe un producto con ese nombre.")
        else:
            messages.error(request, "Error en el formulario. Revise los campos.")
    else:
        form = ProductoForm()
    return render(request, 'pedidos/agregar_producto.html', {'form': form})

def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Producto actualizado con éxito.")
                return redirect('listar_productos')
            except IntegrityError:
                messages.error(request, "Error al actualizar el producto. Ya existe un producto con ese nombre.")
        else:
            messages.error(request, "Error en el formulario. Revise los campos.")
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'pedidos/editar_producto.html', {'form': form})

def eliminar_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, pk=producto_id)
        producto.delete()
        messages.success(request, "Producto eliminado con éxito.")
    except Producto.DoesNotExist:
        messages.error(request, "El producto no existe.")
    return redirect('listar_productos')

def lista_productos(request):
    productos = Producto.objects.all() # Para mejorar el rendimiento, se podría agregar paginación
    return render(request, 'pedidos/lista_productos.html', {'productos': productos})

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    return render(request, 'pedidos/detalle_producto.html', {'producto': producto})



from django.shortcuts import render, redirect
from django.utils import timezone
from django.db import transaction, IntegrityError
from django.contrib import messages
from .forms import ClienteAnonimoForm, PedidoForm
from .models import Pedido, ItemPedido
from django.http import JsonResponse

def crear_pedido(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "El carrito está vacío.")
        return redirect('ver_carrito')

    for producto_id, item in carrito.items():
        if item.get('cantidad', 0) == 0:
            messages.error(request, f"El producto '{item.get('nombre', 'Producto Desconocido')}' tiene cantidad cero. Por favor, actualice la cantidad.")
            return redirect('ver_carrito')

    if request.method == 'POST':
        cliente_form = ClienteAnonimoForm(request.POST)
        pedido_form = PedidoForm(request.POST, request.FILES)

        if cliente_form.is_valid() and pedido_form.is_valid():
            cliente_anonimo = cliente_form.save()
            pedido = pedido_form.save(commit=False)
            pedido.cliente_anonimo = cliente_anonimo
            pedido.fecha_creacion = timezone.now()
            pedido.total = 0

            try:
                with transaction.atomic():
                    pedido.save()
            except IntegrityError:
                pedido = pedido_form.save(commit=False)
                pedido.cliente_anonimo = cliente_anonimo
                pedido.fecha_creacion = timezone.now()
                pedido.total = 0

                with transaction.atomic():
                    last_pedido = Pedido.objects.order_by('-id').first()
                    if last_pedido:
                        pedido.id = last_pedido.id + 1
                    else:
                        if not Pedido.objects.filter(id=1).exists():
                            pedido.id = 1
                        else:
                            last_pedido = Pedido.objects.order_by('-id').first()
                            pedido.id = last_pedido.id + 1
                    pedido.save()

            total_pedido = 0
            for producto_id, item in carrito.items():
                cantidad = int(item.get('cantidad', 1))
                precio_unitario = float(item.get('precio', 0))
                total_pedido += cantidad * precio_unitario
                ItemPedido.objects.create(
                    pedido=pedido,
                    producto_id=producto_id,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario
                )

            cargo_delivery = 500  # Cargo fijo de delivery
            total_con_delivery = total_pedido + cargo_delivery
            pedido.total = total_con_delivery
            pedido.save()

            request.session['carrito'] = {}
            messages.success(request, "Pedido realizado con éxito.")

            # Devuelve una respuesta JSON con el pedido_id
            return JsonResponse({'success': True, 'pedido_id': pedido.id})
        else:
            return JsonResponse({'success': False, 'errors': cliente_form.errors, 'pedido_form_errors': pedido_form.errors})
    else:
        cliente_form = ClienteAnonimoForm()
        pedido_form = PedidoForm()

    subtotal = sum(int(item.get('cantidad', 1)) * float(item.get('precio', 0)) for item in carrito.values())
    cargo_delivery = 500
    total_con_delivery = subtotal + cargo_delivery

    return render(request, 'pedidos/crear_pedido.html', {
        'cliente_form': cliente_form,
        'pedido_form': pedido_form,
        'subtotal': subtotal,
        'cargo_delivery': cargo_delivery,
        'total_con_delivery': total_con_delivery
    })


#def listar_pedidos(request):
    #pedidos = Pedido.objects.all().order_by('-fecha_creacion') # Para mejorar el rendimiento, se podría agregar paginación
    #return render(request, 'pedidos/lista_pedidos.html', {'pedidos': pedidos})
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Pedido

def listar_pedidos(request):
    pedidos_list = Pedido.objects.all().order_by('-fecha_creacion')
    paginator = Paginator(pedidos_list, 10)  # Muestra 10 pedidos por página
    page_number = request.GET.get('page')
    pedidos = paginator.get_page(page_number)
    return render(request, 'pedidos/lista_pedidos.html', {'pedidos': pedidos})


import json
from django.shortcuts import render, get_object_or_404
from .models import Pedido, ItemPedido  # Asegúrate de que las rutas sean correctas

def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    items = ItemPedido.objects.filter(pedido=pedido).select_related('producto')
    print(items)
    items_data = []
    for item in items:
        precio_total = item.cantidad * item.producto.precio  # Calcular precio total aquí
        items_data.append({
            'producto_nombre': item.producto.nombre,
            'cantidad': item.cantidad,
            'precio_unitario': str(item.producto.precio),  # Convertir a cadena
            'precio_total': str(precio_total),  # Agregar precio total y convertir a cadena
        })
    items_json = json.dumps(items_data)
    return render(request, 'pedidos/detalle_pedido.html', {'pedido': pedido, 'items': items, 'items_json': items_json,  'items_data': items_data})

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Pedido, ItemPedido
from django.urls import reverse

def actualizar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    if request.method == 'POST':
        print("Pedido antes de actualizar:", pedido.cliente_anonimo.nombre, pedido.cliente_anonimo.apellido, pedido.direccion)

        # Actualiza los datos del cliente
        pedido.cliente_anonimo.nombre = request.POST.get('nombre')
        pedido.cliente_anonimo.apellido = request.POST.get('apellido')
        pedido.cliente_anonimo.telefono = request.POST.get('telefono')
        pedido.direccion = request.POST.get('direccion')
        pedido.save()
        pedido.cliente_anonimo.save()  # Guarda los cambios en cliente_anonimo
        messages.success(request, "Pedido actualizado con éxito.")

        # Recarga el pedido actualizado de la base de datos
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        print("Pedido después de actualizar:", pedido.cliente_anonimo.nombre, pedido.cliente_anonimo.apellido, pedido.direccion)

        # Recalcula items_data después de actualizar el pedido
        items = ItemPedido.objects.filter(pedido=pedido).select_related('producto')
        items_data = []
        for item in items:
            precio_total = item.cantidad * item.producto.precio
            items_data.append({
                'producto_nombre': item.producto.nombre,
                'cantidad': item.cantidad,
                'precio_unitario': str(item.producto.precio),
                'precio_total': str(precio_total),
            })
        items_json = json.dumps(items_data)

        # Redirige a la página de detalles del pedido con el pedido y items_data actualizados
        url_detalle_pedido = reverse('detalle_pedido', args=[pedido_id])
        return redirect(f'{url_detalle_pedido}#detalle-pedido-ancla')

    # Recalcula items_data en caso de que sea un GET request
    items = ItemPedido.objects.filter(pedido=pedido).select_related('producto')
    items_data = []
    for item in items:
        precio_total = item.cantidad * item.producto.precio
        items_data.append({
            'producto_nombre': item.producto.nombre,
            'cantidad': item.cantidad,
            'precio_unitario': str(item.producto.precio),
            'precio_total': str(precio_total),
        })
    items_json = json.dumps(items_data)

    return render(request, 'pedidos/detalle_pedido.html', {'pedido': pedido, 'items_data': items_data, 'items_json': items_json})
#si se olvidan de cargar algun producto
from django.shortcuts import render, get_object_or_404, redirect
from .models import Pedido, Producto, ItemPedido
from django.contrib import messages
from django.urls import reverse

def agregar_producto_al_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    productos = Producto.objects.all()

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad'))
        producto = get_object_or_404(Producto, pk=producto_id)

        # Agrega el producto al pedido con el precio_unitario
        item_pedido, created = ItemPedido.objects.get_or_create(
            pedido=pedido,
            producto=producto,
            defaults={'cantidad': cantidad, 'precio_unitario': producto.precio}
        )
        if not created:
            item_pedido.cantidad += cantidad
            item_pedido.save()

        messages.success(request, f"{producto.nombre} agregado al pedido.")
        url_detalle_pedido = reverse('detalle_pedido', args=[pedido_id])
        return redirect(f'{url_detalle_pedido}#detalle-pedido-ancla')

    return render(request, 'pedidos/agregar_producto_al_pedido.html', {'pedido': pedido, 'productos': productos})

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .models import ItemPedido

def eliminar_item_pedido(request, item_id):
    item = get_object_or_404(ItemPedido, pk=item_id)
    if request.method == 'POST':
        item.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})



def confirmar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    if request.method == 'POST':
        pedido.estado = 'confirmado'
        pedido.save()
        messages.success(request, "Pedido confirmado,Cuando este en camino le avisaremos. Muchas Gracias.")
        return redirect('home')

@transaction.atomic
def eliminar_pedido(request, pedido_id):
    try:
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        pedido.delete()
        messages.success(request, "Pedido eliminado con éxito.")
    except Pedido.DoesNotExist:
        messages.error(request, "El pedido no existe.")
    return redirect('listar_pedidos')

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from .models import Producto
from decimal import Decimal
from django.contrib import messages
from django.urls import reverse

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    carrito = request.session.get('carrito', {})
    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += 1
    else:
        carrito[str(producto_id)] = {'nombre': producto.nombre, 'precio': float(producto.precio), 'cantidad': 1}
    request.session['carrito'] = carrito

    # Redirige a la vista 'ver_carrito' con el fragmento de URL
    return redirect(reverse('ver_carrito') + '#inicio-carrito')




from django.shortcuts import render
from django.http import HttpRequest
from decimal import Decimal

def ver_carrito(request: HttpRequest):
    """
    Vista para mostrar el carrito de compras.

    Calcula el subtotal de cada producto y el total del carrito.
    Maneja productos inválidos en el carrito con registro de logs.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP con el carrito y el total.
    """
    carrito = request.session.get('carrito', {})
    productos_carrito = []
    total = Decimal('0.00')

    for producto_id, item in carrito.items():
        try:
            cantidad = int(item.get('cantidad', 0))
            precio = Decimal(str(item.get('precio', '0.00')))
            subtotal = precio * cantidad

            productos_carrito.append({
                'producto_id': producto_id,
                'nombre': item.get('nombre', 'Producto Desconocido'),
                'cantidad': cantidad,
                'precio': precio,
                'subtotal': subtotal,
            })
            total += subtotal
        except (ValueError, TypeError) as e:
            print(f"Elemento invalido en el carrito: {item}")

    context = {
        'productos_carrito': productos_carrito,
        'total': total,
    }
    return render(request, 'pedidos/ver_carrito.html', context)

def actualizar_cantidad(request, producto_id):
    carrito_actual = request.session.get('carrito', {})
    if str(producto_id) in carrito_actual:
        cantidad = request.POST.get('cantidad')
        if cantidad and cantidad.isdigit() and int(cantidad) > 0:
            try:
                carrito_nuevo = carrito_actual.copy()
                carrito_nuevo[str(producto_id)]['cantidad'] = int(cantidad)
                request.session['carrito'] = carrito_nuevo
                request.session.modified = True
                messages.success(request, "Cantidad actualizada.")
            except Exception as e:
                messages.error(request, f"Error al actualizar la cantidad: {e}")
        else:
            messages.error(request, "Cantidad no válida.")
    return redirect('ver_carrito')



from django.shortcuts import render, redirect
from django.http import HttpRequest
from decimal import Decimal



from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from decimal import Decimal
from django.contrib import messages

def eliminar_del_carrito(request: HttpRequest, producto_id):
    """
    Elimina un producto del carrito de compras.

    Args:
        request (HttpRequest): La solicitud HTTP.
        producto_id (int): El ID del producto a eliminar.

    Returns:
        HttpResponse: Redirige a la vista del carrito de compras.
    """
    carrito = request.session.get('carrito', {})

    if str(producto_id) in carrito:
        del carrito[str(producto_id)]  # Elimina el producto del carrito
        request.session['carrito'] = carrito
        messages.success(request, "Producto eliminado del carrito.")
    else:
        messages.error(request, "Producto no encontrado en el carrito.")

    # Recalcula los productos del carrito y el total
    productos_carrito = []
    total = Decimal('0.00')
    for prod_id, item in carrito.items():
        try:
            cantidad = int(item.get('cantidad', 0))
            precio = Decimal(str(item.get('precio', '0.00')))
            subtotal = precio * cantidad

            productos_carrito.append({
                'producto_id': prod_id,
                'nombre': item.get('nombre', 'Producto Desconocido'),
                'cantidad': cantidad,
                'precio': precio,
                'subtotal': subtotal,
            })
            total += subtotal
        except (ValueError, TypeError) as e:
            print(f"Elemento invalido en el carrito: {item}")

    context = {
        'productos_carrito': productos_carrito,
        'total': total,
    }
    return render(request, 'pedidos/ver_carrito.html', context)

def actualizar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Producto actualizado con éxito.")
                return redirect('listar_productos')
            except IntegrityError:
                messages.error(request, "Error al actualizar el producto. Ya existe un producto con ese nombre.")
        else:
            messages.error(request, "Error en el formulario. Revise los campos.")
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'pedidos/editar_producto.html', {'form': form})



def vaciar_carrito(request):
    request.session['carrito'] = {}
    return redirect('ver_carrito')

def politica_privacidad(request):
    return render(request, 'pedidos/politica_privacidad.html')

def terminos_condiciones(request):
    return render(request, 'pedidos/terminos_condiciones.html')




def iniciar_sesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirige a la página principal después del inicio de sesión
        else:
            return render(request, 'pedidos/iniciar_sesion.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'pedidos/iniciar_sesion.html')

def cerrar_sesion(request):
    logout(request)
    return redirect('home')  # Redirige a la página principal después del cierre de sesión




from django.http import JsonResponse
from decimal import Decimal

# ... (otras importaciones y funciones)

def actualizar_cantidad_ajax(request, producto_id):
    """
    Actualiza la cantidad de un producto en el carrito y devuelve el nuevo subtotal y total.
    """
    if request.method == 'POST':
        try:
            cantidad = int(json.loads(request.body)['cantidad'])
            if cantidad < 1:
                return JsonResponse({'success': False, 'message': 'Cantidad inválida.'})

            carrito = request.session.get('carrito', {})
            if str(producto_id) in carrito:
                carrito[str(producto_id)]['cantidad'] = cantidad
                request.session['carrito'] = carrito
                request.session.modified = True

                # Recalcular el subtotal y el total
                subtotal = Decimal(carrito[str(producto_id)]['precio']) * cantidad
                total = sum(Decimal(item['precio']) * item['cantidad'] for item in carrito.values())

                return JsonResponse({'success': True, 'subtotal': str(subtotal), 'total': str(total)})
            else:
                return JsonResponse({'success': False, 'message': 'Producto no encontrado en el carrito.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido.'})