from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from productos.models import Producto
from .models import Carrito, ItemCarrito
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Carrito
from tiendas.models import Tienda  
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from productos.models import Producto
from .models import Carrito, ItemCarrito
from tiendas.models import Tienda
# ---> Lógica del carrito de compras reutilizado para los 3 tipos de usuarios.
@login_required
def shopping_cart(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related(
        'producto',
        'producto__tienda'
    )
    # ---> Determinar qué navbar mostrar
    es_vendedor = False
    tienda_inactiva = False
    tienda = Tienda.objects.filter(propietario=request.user).first()
    if tienda:
        if tienda.activo:
            es_vendedor = True
        else:
            tienda_inactiva = True

    return render(request, "carrito/shopping_cart.html", {
        "carrito": carrito,
        "items": items,
        "es_vendedor": es_vendedor,
        "tienda_inactiva": tienda_inactiva
    })
# ---> Lógica Gestión de carrito: agregar producto y validar disponibilidad.
@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    es_vendedor = False
    tienda_inactiva = False
    tienda = Tienda.objects.filter(propietario=request.user).first()
    if tienda:
        if tienda.activo:
            es_vendedor = True
        else:
            tienda_inactiva = True
    if request.method == "POST":
        try:
            cantidad = int(request.POST.get("cantidad", 1))
        except ValueError:
            cantidad = 1
        item, created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={"cantidad": 0}
        )
        cantidad_total = item.cantidad + cantidad
        # ---> VALIDAR STOCK.
        if cantidad_total > producto.stock:
            messages.error(
                request,
                f"No hay suficiente stock de {producto.nombre}. Solo hay {producto.stock - item.cantidad} disponibles."
            )
            return render(request, 'usuarios/buy_product.html', {
                'producto': producto,
                'es_vendedor': es_vendedor,
                'tienda_inactiva': tienda_inactiva,
                'cantidad_actual': item.cantidad
            })
        # ---> CANTIDAD Y EL RESTO ESTEN BIEN.
        item.cantidad = cantidad_total
        item.save()

        messages.success(
            request,
            f"{producto.nombre} agregado al carrito ({cantidad} unidades)."
        )
        return redirect("carrito:shopping_cart")
    return render(request, 'usuarios/buy_product.html', {
        'producto': producto,
        'es_vendedor': es_vendedor,
        'tienda_inactiva': tienda_inactiva,
        'cantidad_actual': 0
    })
@login_required
# ---> Lógica para eliminar un producto del carrito.
def eliminar_producto(request, item_id):
    """Elimina un producto del carrito."""
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    return redirect("carrito:shopping_cart")