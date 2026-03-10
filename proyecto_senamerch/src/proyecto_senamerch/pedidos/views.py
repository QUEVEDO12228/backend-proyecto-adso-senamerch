# pedidos/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Pedido, PedidoItem  # Asumiendo tus modelos
from django.http import Http404

@login_required
def client_orders(request):

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
    """Procesa la compra del carrito y genera un pedido."""
    carrito = Carrito.objects.get(usuario=request.user)
    items = carrito.items.all()

    if not items.exists():
        # Si el carrito está vacío, redirige a la lista de productos
        return redirect('productos:lista_productos')

    # Crear pedido
    pedido = Pedido.objects.create(
        usuario=request.user,
        total=0,
        estado='pending',
        creado_en=timezone.now()
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

    # Vaciar carrito
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

def edit_order(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

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
            # lógica simple: duplicar pedido
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