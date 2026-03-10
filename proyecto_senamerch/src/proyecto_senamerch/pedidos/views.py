# pedidos/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Pedido, PedidoItem  # Asumiendo tus modelos
from django.http import Http404

@login_required
def client_orders(request):
    """
    Vista para mostrar los pedidos del cliente según su estado:
    'pending', 'delivered' o 'canceled'.
    """
    # Obtener el estado del query string; por defecto 'pending'
    status = request.GET.get('status', 'pending')

    # Validar estado
    valid_statuses = ['pending', 'delivered', 'canceled']
    if status not in valid_statuses:
        status = 'pending'

    # Filtrar pedidos del usuario según estado
    pedidos = Pedido.objects.filter(usuario=request.user, estado=status).order_by('-creado_en')

    return render(request, 'pedidos/client_orders.html', {
        'pedidos': pedidos,
        'selected_status': status
    })

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


@login_required
def cancel_order(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    if request.method == "POST":
        pedido.estado = "cancelled"
        pedido.save()
    return redirect('pedidos:client_orders')

@login_required
def edit_order(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    if request.method == "POST":
        # Aquí puedes procesar cambios en el pedido
        # Por ejemplo: actualizar cantidades o estado
        for item in pedido.items.all():
            cantidad = int(request.POST.get(f'cantidad_{item.id}', item.cantidad))
            item.cantidad = cantidad
            item.save()
        # Recalcular total
        total = sum(item.cantidad * item.precio_unitario for item in pedido.items.all())
        pedido.total = total
        pedido.save()
        return redirect('pedidos:client_orders')

    # GET: mostrar formulario de edición
    return render(request, 'pedidos/edit_order.html', {
        'pedido': pedido,
        'items': pedido.items.all()
    })