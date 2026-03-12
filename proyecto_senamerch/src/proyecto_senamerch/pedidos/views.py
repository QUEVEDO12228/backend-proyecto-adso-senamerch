from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from datetime import timedelta
from django.http import HttpResponse
from .models import Pedido, PedidoItem
from carrito.models import Carrito
from tiendas.models import Tienda
# ==================================
#  Pedidos Clientes 
# ==================================
@login_required
def client_orders(request):
    """
    Vista para mostrar los pedidos del cliente según el estado seleccionado (pending, delivered, canceled).
    También muestra el tiempo restante para cancelar un pedido si está en estado 'pending'.
    """
    # Obtener el estado de los pedidos desde la URL, por defecto es 'pending'
    selected_status = request.GET.get('status', 'pending')

    # Filtrar los pedidos según el estado seleccionado
    if selected_status in ['pending', 'delivered', 'canceled']:
        pedidos = Pedido.objects.filter(estado=selected_status, usuario=request.user)
    else:
        # Si el estado no es uno de los permitidos, se filtra por 'pending'
        pedidos = Pedido.objects.filter(estado='pending', usuario=request.user)

    # Calcular el tiempo restante para la cancelación de cada pedido en estado 'pending'
    for pedido in pedidos:
        tiempo_restante = pedido.tiempo_restante_cancelacion()

        if tiempo_restante > 0:
            horas = tiempo_restante // 3600  # Calcular las horas restantes
            minutos = (tiempo_restante % 3600) // 60  # Calcular los minutos restantes
            pedido.horas_restantes = horas
            pedido.minutos_restantes = minutos
        else:
            pedido.horas_restantes = 0
            pedido.minutos_restantes = 0

    # Contexto para pasar a la plantilla
    context = {
        'pedidos': pedidos,
        'selected_status': selected_status
    }
    
    return render(request, 'pedidos/client_orders.html', context)
# =========================
#  Editar Pedido Cliente
# =========================
@login_required
def edit_order(request, pedido_id):
    """ Permite al usuario editar un pedido, modificar el tipo de entrega, cancelar el pedido, o realizar un nuevo pedido con los mismos productos (recomprar). """
    # Obtén el pedido del usuario logueado
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    # Verificar si el pedido puede ser editado (debe ser en estado "pending")
    if not pedido.puede_editar():
        return redirect("pedidos:client_orders")  # Redirige si no se puede editar
    # Obtener la tienda asociada al primer producto del pedido
    first_item = pedido.items.first()
    tienda = first_item.producto.tienda if first_item else None
    if request.method == "POST":
        # Procesar cambios en el tipo de entrega
        tipo_entrega = request.POST.get("tipo_entrega")
        if tipo_entrega:
            pedido.tipo_entrega = tipo_entrega
            pedido.save()
        # Cancelar pedido
        if "cancelar" in request.POST:
            pedido.estado = "canceled"
            pedido.save()
            return redirect("pedidos:client_orders")
        # Marcar pedido como pendiente nuevamente (si estaba en estado entregado)
        if "realizar" in request.POST:
            pedido.estado = "pending"
            pedido.save()
            return redirect("pedidos:client_orders")
        # Crear un nuevo pedido con los mismos productos (recomprar)
        if "recomprar" in request.POST:
            nuevo_pedido = Pedido.objects.create(
                usuario=request.user,
                estado="pending",
                tipo_entrega=pedido.tipo_entrega
            )
            for item in pedido.items.all():
                PedidoItem.objects.create(
                    pedido=nuevo_pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario
                )
            return redirect("pedidos:client_orders")
    # Contexto para pasar el pedido y la tienda a la plantilla
    context = {
        "pedido": pedido,
        "tienda": tienda
    }
    return render(request, "pedidos/edit_order.html", context)
# ==================================
#  Detalles de los pedidos clientes
# ==================================
@login_required
def view_purchase(request, pedido_id):
    """ Vista para ver los detalles de un pedido específico, incluyendo los productos y el total. Solo se permite ver pedidos entregados. """
    # Obtener el pedido o devolver 404 si no existe o no pertenece al usuario
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    # Verificar si el estado del pedido es 'delivered'
    if pedido.estado != 'delivered':
        return redirect("pedidos:client_orders")
    # Obtener los ítems del pedido
    items = PedidoItem.objects.filter(pedido=pedido)
    # Calcular base, IVA y total
    base = sum(item.precio_unitario * item.cantidad for item in items)
    iva = base * 0.19
    total = base + iva
    return render(request, 'pedidos/view_purchases.html', {
        'pedido': pedido,
        'items': items,
        'base': base,
        'iva': iva,
        'total': total
    })
# ==========================
#  Crear una compra cliente
# ==========================
@login_required
def buy_cart(request):
    """ Vista para crear un pedido a partir de los artículos del carrito de compras. El carrito se vacía después de crear el pedido. """
    try:
        # Obtener el carrito del usuario (manejar excepciones si no existe)
        carrito = Carrito.objects.get(usuario=request.user)
    except Carrito.DoesNotExist:
        messages.error(request, 'No tienes un carrito de compras.')
        return redirect('productos:lista_productos')
    # Obtener los artículos del carrito
    items = carrito.items.all()
    # Verificar si el carrito está vacío
    if not items.exists():
        messages.error(request, 'Tu carrito está vacío. Agrega productos antes de realizar un pedido.')
        return redirect('productos:lista_productos')
    # Crear un nuevo pedido
    pedido = Pedido.objects.create(
        usuario=request.user,
        total=0,
        estado='pending'
    )
    total = 0
    # Crear los items del pedido y calcular el total
    for item in items:
        PedidoItem.objects.create(
            pedido=pedido,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=item.producto.precio
        )
        total += item.subtotal()  # Aquí llamas al método 'subtotal' del carrito para calcular el precio total por producto.
    # Asignar el total al pedido y guardarlo
    pedido.total = total
    pedido.save()
    # Eliminar los items del carrito después de realizar el pedido
    items.delete()
    # Redirigir al usuario a la lista de pedidos
    return redirect('pedidos:client_orders')
# ================
#  Método de pago
# ================
@login_required
def option_payment_method(request):
    """ Vista para seleccionar el método de pago. Crea un pedido con los artículos del carrito y lo asocia a la tienda del primer producto. El carrito se limpia después de crear el pedido. """
    # Obtener el carrito del usuario actual
    carrito = Carrito.objects.get(usuario=request.user)
    items = carrito.items.all()
    if request.method == "POST":
        # Verificar que el carrito no esté vacío
        if not items.exists():
            return redirect('productos:lista_productos')  # Redirigir si el carrito está vacío
        # Obtener la tienda asociada al primer producto del carrito
        tienda = items.first().producto.tienda
        if not tienda:
            return redirect('productos:lista_productos')  # Redirigir si no se encuentra la tienda
        # Crear un nuevo pedido en estado "pending"
        pedido = Pedido.objects.create(
            usuario=request.user,
            tienda=tienda,  # Asociamos la tienda al pedido
            total=0,
            estado='pending'
        )
        total = 0
        # Crear los items del pedido y calcular el total
        for item in items:
            PedidoItem.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio
            )
            total += item.subtotal()  # Sumamos el subtotal del producto al total
        # Actualizar el total del pedido
        pedido.total = total
        pedido.save()
        # Limpiar el carrito después de crear el pedido
        items.delete()
        # Redirigir al usuario a la página de pedidos
        return redirect('pedidos:client_orders')
    return render(request, 'carrito/option_payment_method.html', {"carrito": carrito})
# ==========================
#  Cancelar Pedido Cliente
# ==========================
@login_required
def cancel_order(request, pedido_id):
    """ Vista para cancelar un pedido. Cambia el estado del pedido a 'canceled' y redirige al cliente a la página de pedidos cancelados. """
    # Obtener el pedido o devolver 404 si no existe o no pertenece al usuario
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    if request.method == "POST":
        # Cambiar el estado del pedido a 'canceled'
        pedido.estado = "canceled"
        pedido.save()
    # Redirigir a la página de pedidos con estado 'canceled'
    url = reverse("pedidos:client_orders")
    return redirect(f"{url}?status=canceled")
# ======================================================
#  Actualizar a estado pendiente, entregado o cancelado
# ======================================================
@login_required
def update_order_status(request, pedido_id):
    """ Permite al vendedor actualizar el estado de un pedido (marcarlo como entregado)."""
    # Obtén el pedido, asegurándote de que el vendedor sea el propietario de la tienda del producto
    pedido = get_object_or_404(Pedido, id=pedido_id)
    # Verificar si el vendedor puede modificar este pedido
    if not pedido.items.filter(producto__tienda__propietario=request.user).exists():
        messages.error(request, "No puedes modificar este pedido.")
        return redirect("pedidos:store_orders")
    if request.method == "POST":
        if pedido.estado == "pending":
            # Marcar el pedido como entregado
            pedido.estado = "delivered"
            pedido.save()
            messages.success(request, f"Pedido #{pedido.id} entregado correctamente")
        else:
            # Avisar si el pedido ya ha sido procesado
            messages.warning(request, "Este pedido ya fue procesado")
    return redirect("pedidos:store_orders")
# ========================
#  Pedidos De La Tienda
# ========================
@login_required
def store_orders(request):
    """ Vista que muestra los pedidos de la tienda del vendedor, filtrados por estado. """
    estado = request.GET.get('estado', 'pending')  # Estado seleccionado (por defecto "pending")
    # Filtrar los pedidos por estado y por tienda del vendedor logueado
    if estado in ['pending', 'delivered', 'canceled']:
        pedidos = Pedido.objects.filter(
            items__producto__tienda__propietario=request.user,  # Filtra por la tienda del vendedor
            estado=estado
        ).distinct()  # Evita duplicados de pedidos si un pedido tiene varios productos
    else:
        # Si el estado no es válido, mostramos todos los pedidos de la tienda
        pedidos = Pedido.objects.filter(
            items__producto__tienda__propietario=request.user
        ).distinct()
    return render(request, 'pedidos/store_orders.html', {'pedidos': pedidos})
# ==================================
#  Pedido Especifico de la tienda
# ==================================
@login_required
def store_order_detail(request, pedido_id):
    """ Vista que muestra los detalles de un pedido específico de la tienda, incluyendo los productos y el total de la compra. """
    # Obtén el pedido solo si pertenece a la tienda del vendedor logueado
    pedido = get_object_or_404(Pedido, id=pedido_id, items__producto__tienda__propietario=request.user)
    # Obtener los items del pedido
    items = pedido.items.all()
    # Calcular el total sumando los subtotales de los productos
    total = sum(item.subtotal() for item in items)
    return render(request, 'pedidos/store_order_detail.html', {
        'pedido': pedido,
        'items': items,
        'total': total,
    })
# =========================
#  Cancelar Pedido Tienda
# =========================
@login_required
def cancel_order_store(request, pedido_id):
    """ Permite al vendedor cancelar un pedido en estado "pending """
    if request.method == "POST":
        # Obtener el pedido solo si pertenece a la tienda del vendedor logueado
        pedido = get_object_or_404(Pedido, id=pedido_id, items__producto__tienda__propietario=request.user)
        # Si el pedido está en estado 'pending', cambiar su estado a 'canceled'
        if pedido.estado == 'pending':
            pedido.estado = 'canceled'
            pedido.save()
    return redirect('pedidos:store_orders')
# ===============================================================
#  Actualizar estado del pedido Pendiente, Entregado, Cancelado
# ===============================================================
@login_required
def deliver_order_store(request, pedido_id):
    """ Permite al vendedor marcar un pedido como entregado. """
    if request.method == "POST":
        # Obtener el pedido solo si pertenece a la tienda del vendedor logueado
        pedido = get_object_or_404(Pedido, id=pedido_id, items__producto__tienda__propietario=request.user)
        # Si el pedido está en estado 'pending', cambiarlo a 'delivered'
        if pedido.estado == 'pending':
            pedido.estado = 'delivered'
            pedido.save()
    return redirect('pedidos:store_orders')