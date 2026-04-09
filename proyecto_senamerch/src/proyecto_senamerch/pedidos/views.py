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
from django.utils.timezone import localtime
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from pedidos.models import Pedido
from productos.models import Producto
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import Pedido
#  # ---> Lógica para los Pedidos Clientes o del vendedor.
@login_required
def client_orders(request):
    """
    Vista que muestra los pedidos del usuario actual (cliente),
    filtrados por estado: pending, delivered, canceled.
    """
    ESTADOS_VALIDOS = ["pending", "delivered", "canceled"]
    selected_status = request.GET.get("status", "pending")
    if selected_status not in ESTADOS_VALIDOS:
        selected_status = "pending"
    # ---> Traemos solo los pedidos donde el usuario es el cliente
    pedidos = Pedido.objects.filter(
        usuario=request.user,
        estado=selected_status
    ).prefetch_related("items__producto__tienda").order_by("-creado_en")
    # ---> Calculamos el tiempo restante para cancelar
    for pedido in pedidos:
        pedido.horas_restantes = 0
        pedido.minutos_restantes = 0
        if pedido.estado == "pending":
            tiempo_restante = pedido.tiempo_restante_cancelacion()
            if tiempo_restante > 0:
                pedido.horas_restantes = int(tiempo_restante // 3600)
                pedido.minutos_restantes = int((tiempo_restante % 3600) // 60)
    # ---> Determinar si el usuario es vendedor o tiene tienda inactiva
    es_vendedor = False
    tienda_inactiva = False
    tienda = Tienda.objects.filter(propietario=request.user).first()
    if tienda:
        if tienda.activo:
            es_vendedor = True
        else:
            tienda_inactiva = True
    return render(request, "pedidos/client_orders.html", {
        "pedidos": pedidos,
        "selected_status": selected_status,
        "es_vendedor": es_vendedor,
        "tienda_inactiva": tienda_inactiva,
    })
# ---> Lógica para Editar Pedido Cliente
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
# ==========================
# ---> Lógica para Crear una compra cliente
from collections import defaultdict
@login_required
def buy_cart(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    items = carrito.items.select_related("producto__tienda")
    if not items.exists():
        return redirect('productos:lista_productos')
    # ---> AGRUPAR ITEMS POR TIENDA
    tiendas_items = defaultdict(list)
    for item in items:
        tiendas_items[item.producto.tienda].append(item)
    pedidos_creados = []
    # ---> CREAR UN PEDIDO POR TIENDA
    for tienda, items_tienda in tiendas_items.items():
        pedido = Pedido.objects.create(
            usuario=request.user,
            tienda=tienda,
            total=0,
            estado='pending'
        )
        total = 0
        for item in items_tienda:
            PedidoItem.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio
            )
            total += item.subtotal()
        pedido.total = total
        pedido.save()
        pedidos_creados.append(pedido)
    # ---> VACIAR CARRITO
    items.delete()
    return redirect('pedidos:client_orders')
# ---> Lógica para el Método de pago
from collections import defaultdict
from django.shortcuts import redirect, get_object_or_404
@login_required
def option_payment_method(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    items = carrito.items.select_related("producto__tienda")
    if request.method == "POST":
        if not items.exists():
            return redirect("productos:lista_productos")
        tiendas = defaultdict(list)
        for item in items:
            tienda = item.producto.tienda
            tiendas[tienda].append(item)
        for tienda, items_tienda in tiendas.items():
            pedido = Pedido.objects.create(
                usuario=request.user,
                tienda=tienda,
                estado="pending",
                total=0
            )
            total = 0
            for item in items_tienda:
                PedidoItem.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio
                )
                total += item.subtotal()
            pedido.total = total
            pedido.save()
        # ---> limpiar carrito
        items.delete()

        # ---> mensaje
        messages.success(request, "Pedido realizado correctamente.")

        # ---> redirect (correcto)
        return redirect("pedidos:client_orders")

    return render(request, "carrito/option_payment_method.html", {
        "carrito": carrito
    })
# ---> Lógica para Cancelar Pedido Cliente
@login_required
def cancel_order(request, pedido_id):
    """ Vista para cancelar un pedido. """
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    if request.method == "POST":
        pedido.estado = "canceled"
        pedido.save()
        # ---> ALERTA
        messages.success(request, "Pedido cancelado correctamente.")
    url = reverse("pedidos:client_orders")
    return redirect(f"{url}?status=canceled")
# ---> Lógica para Actualizar a estado pendiente, entregado o cancelado
@login_required
def update_order_status(request, pedido_id):
    """ Permite al vendedor actualizar el estado de un pedido (marcarlo como entregado)."""
    # ---> Obtén el pedido, asegurándote de que el vendedor sea el propietario de la tienda del producto
    pedido = get_object_or_404(Pedido, id=pedido_id)
    # ---> Verificar si el vendedor puede modificar este pedido
    if not pedido.items.filter(producto__tienda__propietario=request.user).exists():
        messages.error(request, "No puedes modificar este pedido.")
        return redirect("pedidos:store_orders")
    if request.method == "POST":
        if pedido.estado == "pending":
            # ---> Marcar el pedido como entregado
            pedido.estado = "delivered"
            pedido.save()
            messages.success(request, f"Pedido #{pedido.id} entregado correctamente")
        else:
            # ---> Avisar si el pedido ya ha sido procesado
            messages.warning(request, "Este pedido ya fue procesado")
    return redirect("pedidos:store_orders")
# ---> Lógica Pedidos De La Tienda
@login_required
def store_orders(request):
    """ Vista que muestra los pedidos de la tienda del vendedor, filtrados por estado. """
    estado = request.GET.get('estado', 'pending')  # ---> Estado seleccionado (por defecto "pending")
    # ---> Filtrar los pedidos por estado y por tienda del vendedor logueado
    if estado in ['pending', 'delivered', 'canceled']:
        pedidos = Pedido.objects.filter(
            items__producto__tienda__propietario=request.user,  # ---> Filtra por la tienda del vendedor
            estado=estado
        ).distinct()  # ---> Evita duplicados de pedidos si un pedido tiene varios productos
    else:
        # ---> Si el estado no es válido, mostramos todos los pedidos de la tienda
        pedidos = Pedido.objects.filter(
            items__producto__tienda__propietario=request.user
        ).distinct()
    return render(request, 'pedidos/store_orders.html', {'pedidos': pedidos})
# ---> Lógica de Pedido Especifico de la tienda
@login_required
def store_order_detail(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    items = pedido.items.all()
    total = pedido.total
    # ---> OBTENER DIRECCIÓN DEL CLIENTE
    address = pedido.usuario.addresses.last()  # ---> usa la última dirección guardada
    return render(request, "pedidos/store_order_detail.html", {
        "pedido": pedido,
        "items": items,
        "total": total,
        "address": address,  # ---> IMPORTANTE
    })
# ---> Lógica para Cancelar Pedido Tienda
@login_required
def cancel_order_store(request, pedido_id):
    if request.method == "POST":
        # ---> usar tienda en vez de items (SIN duplicados)
        pedido = get_object_or_404(
            Pedido,
            id=pedido_id,
            tienda__propietario=request.user
        )
        if pedido.estado == 'pending':
            pedido.estado = 'canceled'
            pedido.save()
            messages.success(request, "Pedido cancelado correctamente.")
        else:
            messages.error(request, "Este pedido no se puede cancelar.")
    url = reverse('pedidos:store_orders')
    return redirect(f"{url}?estado=canceled")
# ---> Lógica para Actualizar estado del pedido Pendiente, Entregado, Cancelado
@login_required
@transaction.atomic
def deliver_order_store(request, pedido_id):
    """
    Vista para marcar un pedido de la tienda como 'Entregado'.
    Solo permite pedidos que estén en estado 'pending'.
    Descuenta el stock de los productos involucrados.
    """
    # ---> Obtener pedido correctamente (SIN joins problemáticos)
    pedido = get_object_or_404(
        Pedido,
        id=pedido_id,
        tienda__propietario=request.user
    )
    if request.method == "POST":

        # ---> Validar estado
        if pedido.estado != "pending":
            messages.error(
                request,
                "Este pedido no se puede entregar porque ya no está pendiente."
            )
            return redirect("pedidos:store_orders")
        # ---> Traer items con productos optimizado
        items = pedido.items.select_related("producto")
        # ---> Descontar stock
        try:
            for item in items:
                item.producto.reducir_stock(item.cantidad)
        except ValueError as e:
            messages.error(
                request,
                f"No se puede entregar el pedido: {str(e)}"
            )
            return redirect("pedidos:store_orders")
        # ---> Cambiar estado
        pedido.estado = "delivered"
        pedido.save()
        # ---> Mensaje éxito
        messages.success(
            request,
            f"Pedido #{pedido.id} entregado correctamente y stock actualizado."
        )
    # ---> Redirección final
    return redirect("pedidos:store_orders")
# ---> Lógica para los Detalles de los pedidos clientes
@login_required
def view_purchase(request, pedido_id):
    pedido = get_object_or_404(
        Pedido,
        id=pedido_id,
        usuario=request.user
    )
    if pedido.estado != "delivered":
        return redirect("pedidos:client_orders")
    fecha_local = localtime(pedido.creado_en)
    pedido_data = {
        "id": pedido.id,
        "fecha": fecha_local.strftime("%d/%m/%Y"),
        "hora": fecha_local.strftime("%H:%M"),
        "tienda": pedido.items.first().producto.tienda.nombre,
        "items": [
            {
                "producto": item.producto.nombre,
                "cantidad": item.cantidad,
                "precio": f"{item.producto.precio_con_descuento:.2f}",
                "descuento": f"{item.producto.descuento}%",
                "total": f"{item.subtotal_con_descuento:.2f}",
            }
            for item in pedido.items.all()
        ],
        "total": f"{pedido.total:.2f}",
    }
    context = {
        "pedido": pedido,
        "pedido_json": pedido_data,
    }
    return render(request, "pedidos/purchase_detail.html", context)
# ---> Lógica...
@login_required
def seller_orders(request):
    ESTADOS_VALIDOS = ["pending", "delivered", "canceled"]
    selected_status = request.GET.get("status", "pending")
    if selected_status not in ESTADOS_VALIDOS:
        selected_status = "pending"

    # Obtener la tienda del vendedor
    tienda = Tienda.objects.filter(propietario=request.user).first()

    # Pedidos que incluyen productos de su tienda
    pedidos = Pedido.objects.filter(
        items__producto__tienda=tienda,
        estado=selected_status
    ).distinct().prefetch_related("items__producto__tienda").order_by("-creado_en")

    # Calcular tiempo restante de cancelación
    for pedido in pedidos:
        pedido.horas_restantes = 0
        pedido.minutos_restantes = 0
        if pedido.estado == "pending":
            tiempo_restante = pedido.tiempo_restante_cancelacion()
            if tiempo_restante > 0:
                pedido.horas_restantes = tiempo_restante // 3600
                pedido.minutos_restantes = (tiempo_restante % 3600) // 60

    context = {
        "pedidos": pedidos,
        "selected_status": selected_status,
    }
    return render(request, "pedidos/client_orders.html", context)