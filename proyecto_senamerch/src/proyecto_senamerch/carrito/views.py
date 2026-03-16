from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from productos.models import Producto
from .models import Carrito, ItemCarrito

@login_required
def shopping_cart(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related(
        'producto',
        'producto__tienda'
    )
    return render(request, "carrito/shopping_cart.html", {
        "carrito": carrito,
        "items": items
    })
@login_required
def agregar_al_carrito(request, producto_id):
    print("POST recibido:", request.method)
    print("Usuario:", request.user)
    print("Producto ID:", producto_id)
    
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    if request.method == "POST":
        cantidad = int(request.POST.get("cantidad", 1))
        print("Cantidad:", cantidad)
        item, created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={"cantidad": cantidad}
        )
        if not created:
            item.cantidad += cantidad
            item.save()
        print("Items en carrito:", list(carrito.items.all()))

    return redirect("carrito:shopping_cart")
@login_required
def eliminar_producto(request, item_id):
    """Elimina un producto del carrito."""
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    return redirect("carrito:shopping_cart")