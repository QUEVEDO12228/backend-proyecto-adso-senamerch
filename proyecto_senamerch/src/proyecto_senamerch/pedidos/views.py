# pedidos/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Pedido, PedidoItem  # Asumiendo tus modelos
from django.http import Http404
from django.utils import timezone
from datetime import timedelta
from tiendas.models import Tienda
@login_required
def client_orders(request):

    # cancelar pedidos con más de 6 horas
    pedidos_expirados = Pedido.objects.filter(
        estado="pending",
        creado_en__lt=timezone.now() - timedelta(hours=6)
    )

    pedidos_expirados.update(estado="canceled")

    status = request.GET.get("status", "pending")

    estados_validos = ["pending", "delivered", "canceled"]
    if status not in estados_validos:
        status = "pending"

    pedidos = Pedido.objects.filter(
        usuario=request.user,
        estado=status
    ).order_by("-creado_en")

    context = {
        "pedidos": pedidos,
        "selected_status": status
    }

    return render(request, "pedidos/client_orders.html", context)
@login_required
def view_purchase(request, pedido_id):
    """
    Vista para mostrar los detalles de una compra entregada.
    Solo se permite ver si el pedido pertenece al usuario y está entregado.
    """
    # Obtener pedido, o 404 si no existe
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    # Validar que el pedido esté entregado
    if pedido.estado != 'delivered':
        raise Http404("Solo se pueden ver compras entregadas.")

    # Obtener los items del pedido
    items = PedidoItem.objects.filter(pedido=pedido)

    # Calcular totales
    base = sum(item.precio_unitario * item.cantidad for item in items)
    iva = base * 0.19  # ejemplo de 19% de IVA
    total = base + iva

    return render(request, 'pedidos/view_purchases.html', {
        'pedido': pedido,
        'items': items,
        'base': base,
        'iva': iva,
        'total': total
    })

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from carrito.models import Carrito
from .models import Pedido, PedidoItem

@login_required
def buy_cart(request):

    carrito = Carrito.objects.get(usuario=request.user)
    items = carrito.items.all()

    if not items.exists():
        return redirect('productos:lista_productos')

    # obtener tienda del primer producto
    first_item = items.first()
    tienda = first_item.producto.tienda

    pedido = Pedido.objects.create(
        usuario=request.user,
        tienda=tienda,
        total=0,
        estado='pending'
    )

    total = 0

    for item in items:

        PedidoItem.objects.create(
            pedido=pedido,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=item.producto.precio
        )

        total += item.subtotal()

    pedido.total = total
    pedido.save()

    items.delete()

    return redirect('pedidos:client_orders')
@login_required
def option_payment_method(request):
    """Muestra la página de métodos de pago y procesa la compra."""
    carrito = Carrito.objects.get(usuario=request.user)
    items = carrito.items.all()

    if request.method == "POST":
        if not items.exists():
            return redirect('productos:lista_productos')  # carrito vacío

        # Crear pedido
        pedido = Pedido.objects.create(usuario=request.user, total=0, estado='pending', creado_en=timezone.now())
        total = 0

        for item in items:
            PedidoItem.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio
            )
            total += item.subtotal()

        pedido.total = total
        pedido.save()

        # Vaciar el carrito
        items.delete()

        # Redirigir al listado de pedidos del cliente
        return redirect('pedidos:client_orders')

    return render(request, 'carrito/option_payment_method.html', {"carrito": carrito})


from django.shortcuts import redirect
from django.urls import reverse

@login_required
def cancel_order(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    if request.method == "POST":
        pedido.estado = "canceled"
        pedido.save()

    url = reverse("pedidos:client_orders")
    return redirect(f"{url}?status=canceled")
@login_required
def edit_order(request, pedido_id):

    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    # ❌ si pasaron más de 2 horas no se puede editar
    if not pedido.puede_editar():
        return redirect("pedidos:client_orders")

    # Obtener tienda del primer producto
    first_item = pedido.items.first()
    tienda = first_item.producto.tienda if first_item else None

    if request.method == "POST":

        tipo_entrega = request.POST.get("tipo_entrega")

        if tipo_entrega:
            pedido.tipo_entrega = tipo_entrega
            pedido.save()

        if "cancelar" in request.POST:
            pedido.estado = "canceled"
            pedido.save()
            return redirect("pedidos:client_orders")

        if "realizar" in request.POST:
            pedido.estado = "pending"
            pedido.save()
            return redirect("pedidos:client_orders")

        if "recomprar" in request.POST:

            nuevo_pedido = Pedido.objects.create(
                usuario=request.user,
                estado="pending",
                tipo_entrega=pedido.tipo_entrega
            )

            for item in pedido.items.all():
                item.pk = None
                item.pedido = nuevo_pedido
                item.save()

            return redirect("pedidos:client_orders")

    context = {
        "pedido": pedido,
        "tienda": tienda
    }

    return render(request, "pedidos/edit_order.html", context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Pedido, ItemPedido
from tiendas.models import Tienda
from django.contrib import messages

@login_required
def store_orders(request):
    try:
        # Obtenemos la tienda del usuario logueado
        tienda = Tienda.objects.get(propietario=request.user)
    except Tienda.DoesNotExist:
        messages.error(request, "No tienes una tienda asociada.")
        return redirect('home')

    # Filtrado por estado
    estado = request.GET.get('estado')
    pedidos = Pedido.objects.filter(items__producto__tienda=tienda).distinct()

    if estado:
        pedidos = pedidos.filter(estado=estado)

    context = {
        "pedidos": pedidos,
    }
    return render(request, "pedidos/store_orders.html", context)


@login_required
def update_order_status(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Verificamos que el pedido tenga productos de la tienda del usuario
    if not pedido.items.filter(producto__tienda__propietario=request.user).exists():
        messages.error(request, "No puedes actualizar este pedido.")
        return redirect('pedidos:store_orders')

    # Solo se puede realizar si está pendiente
    if pedido.estado == "pending":
        pedido.estado = "delivered"
        pedido.save()
        messages.success(request, f"Pedido #{pedido.id} marcado como entregado.")
    else:
        messages.info(request, f"Pedido #{pedido.id} ya estaba entregado.")

    return redirect('pedidos:store_orders')