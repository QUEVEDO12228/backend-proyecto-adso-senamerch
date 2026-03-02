from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from tiendas.models import Tienda
from .models import Producto, ImagenProducto
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from comentarios.models import Comentario

# 🔹 PASO 1
@login_required
def create_product(request):
    if request.method == "POST":
        categoria = request.POST.get("categoria")

        if not categoria:
            return redirect("productos:create_product")

        request.session['product_data'] = {
            "nombre": request.POST.get("name"),
            "precio": request.POST.get("price"),
            "categoria": request.POST.get("categoria"),
            "unidad": request.POST.get("unit"),
        }

        return redirect("productos:create_product_step2")

    return render(request, "productos/create_product.html")


# 🔹 PASO 2
@login_required
def create_product_step2(request):
    if request.method == "POST":

        product_data = request.session.get("product_data", {})

        product_data["discount"] = request.POST.get("discount")
        product_data["expiration_date"] = request.POST.get("expiration_date")
        product_data["payment_method"] = request.POST.get("payment_method")

        request.session["product_data"] = product_data

        return redirect("productos:create_product_step3")

    return render(request, "productos/create_product2.html")


# 🔹 PASO 3
@login_required
def create_product_step3(request):
    if request.method == "POST":

        product_data = request.session.get("product_data", {})

        product_data.update({
            "descripcion": request.POST.get("description"),
            "tipo_envio": request.POST.get("shipping_type"),
        })

        request.session["product_data"] = product_data

        return redirect("productos:create_product_step4")

    return render(request, "productos/create_product3.html")


# 🔹 PASO 4 (CREACIÓN FINAL)


@login_required
def create_product_step4(request):

    if request.method == "POST":

        product_data = request.session.get("product_data")

        if not product_data:
            return redirect("productos:create_product")

        tienda = Tienda.objects.filter(propietario=request.user).first()

        if not tienda:
            return redirect("tiendas:create_store")

        # 🔥 CREAR PRODUCTO
        producto = Producto.objects.create(
            tienda=tienda,
            nombre=product_data.get("nombre"),
            precio=product_data.get("precio"),
            categoria=product_data.get("categoria") or "otros",
            unidad_medida=product_data.get("unidad") or "kg",
            tipo_producto="solido",
            descuento=product_data.get("discount") or 0,
            fecha_caducidad=product_data.get("expiration_date") or datetime.now().date(),
            metodo_pago=product_data.get("payment_method") or "efectivo",
            tipo_envio=product_data.get("tipo_envio") or "contraentrega",
            descripcion=product_data.get("descripcion") or "",
        )

        # 🔥 DEBUG (puedes borrar después)
        print("FILES RECIBIDOS:", request.FILES)

        # 🔥 GUARDAR IMÁGENES
        imagenes_guardadas = 0

        for i in range(1, 7):
            imagen = request.FILES.get(f"image{i}")
            if imagen:
                ImagenProducto.objects.create(
                    producto=producto,
                    imagen=imagen
                )
                imagenes_guardadas += 1

        print(f"Imágenes guardadas: {imagenes_guardadas}")
        print("FILES:", request.FILES)

        # 🔥 LIMPIAR SESIÓN
        request.session.pop("product_data", None)

        return redirect("tiendas:seller_catalog")

    return render(request, "productos/create_product4.html")

def edit_product_seller(request, id):
    producto = Producto.objects.get(id=id)

    if request.method == "POST":
        # lógica de edición
        pass

    return render(request, "tiendas/edit_product.html", {
        "producto": producto
    })
# ===============================
# 🔹 PASO 1 EDITAR
# ===============================
@login_required
def edit_product_seller(request, id):
    producto = get_object_or_404(Producto, id=id, tienda__propietario=request.user)

    if request.method == "POST":
        request.session["edit_product_data"] = {
            "nombre": request.POST.get("name"),
            "precio": request.POST.get("price"),
            "categoria": request.POST.get("categoria"),
            "unidad": request.POST.get("unit"),
        }

        return redirect("productos:edit_product_step2", id=id)

    return render(request, "productos/edit_product_seller.html", {
        "producto": producto
    })


# ===============================
# 🔹 PASO 2 EDITAR
# ===============================
@login_required
def edit_product_step2(request, id):
    producto = get_object_or_404(Producto, id=id, tienda__propietario=request.user)

    if request.method == "POST":

        data = request.session.get("edit_product_data", {})

        data["tipo_producto"] = request.POST.get("tipo_producto")
        data["descuento"] = request.POST.get("discount")
        data["fecha_caducidad"] = request.POST.get("expiration_date")
        data["metodo_pago"] = request.POST.get("payment_method")

        request.session["edit_product_data"] = data

        return redirect("productos:edit_product_step3", id=id)

    return render(request, "productos/edit_product_seller2.html", {
        "producto": producto
    })


# ===============================
# 🔹 PASO 3 EDITAR
# ===============================
@login_required
def edit_product_step3(request, id):
    producto = get_object_or_404(Producto, id=id, tienda__propietario=request.user)

    if request.method == "POST":

        data = request.session.get("edit_product_data", {})

        data["descripcion"] = request.POST.get("description")
        data["tipo_envio"] = request.POST.get("shipping_type")

        request.session["edit_product_data"] = data

        return redirect("productos:edit_product_step4", id=id)

    return render(request, "productos/edit_product_seller3.html", {
        "producto": producto
    })


# ===============================
# 🔹 PASO 4 EDITAR (GUARDAR)
# ===============================
@login_required
def edit_product_step4(request, id):

    producto = get_object_or_404(
        Producto,
        id=id,
        tienda__propietario=request.user
    )

    # 🔥 OBTENER IMÁGENES ORDENADAS
    imagenes = producto.imagenes.order_by("id")

    if request.method == "POST":

        data = request.session.get("edit_product_data")

        if not data:
            return redirect("productos:edit_product_seller", id=id)

        # 🔥 ACTUALIZAR PRODUCTO
        producto.nombre = data.get("nombre")
        producto.precio = data.get("precio")
        producto.categoria = data.get("categoria")
        producto.unidad_medida = data.get("unidad")
        producto.tipo_producto = data.get("tipo_producto")
        producto.descuento = data.get("descuento") or 0
        producto.fecha_caducidad = data.get("fecha_caducidad")
        producto.metodo_pago = data.get("metodo_pago")
        producto.tipo_envio = data.get("tipo_envio")
        producto.descripcion = data.get("descripcion")

        producto.save()

        imagenes_actuales = list(imagenes)

        for i in range(1, 7):
            nueva_imagen = request.FILES.get(f"image{i}")

            if nueva_imagen:
                if len(imagenes_actuales) >= i:

                    imagen_obj = imagenes_actuales[i - 1]

                    if imagen_obj.imagen:
                        imagen_obj.imagen.delete(save=False)

                    imagen_obj.imagen = nueva_imagen
                    imagen_obj.save()

                else:
                    ImagenProducto.objects.create(
                        producto=producto,
                        imagen=nueva_imagen
                    )

        request.session.pop("edit_product_data", None)

        return redirect("tiendas:seller_catalog")

    # 🔥 IMPORTANTE: PASAMOS IMÁGENES
    return render(request, "productos/edit_product_seller4.html", {
        "producto": producto,
        "imagenes": imagenes
    })

@login_required
def description_product_seller(request, id):
    producto = get_object_or_404(Producto, id=id)
    
    if request.method == "POST":
        texto = request.POST.get("comentario", "").strip()
        if texto:
            Comentario.objects.create(
                producto=producto,
                usuario=request.user,
                texto=texto
            )
            return redirect('productos:description_product_seller', id=producto.id)

    comentarios = producto.comentarios.order_by('-creado_en')  # Relacion inversa

    return render(request, "productos/description_product_seller.html", {
        "producto": producto,
        "comentarios": comentarios
    })

def description_product_client(request, id):
    producto = get_object_or_404(Producto, id=id)

    return render(request, "productos/description_product_client.html", {
        "producto": producto
    })
def buy_product(request, id):
    producto = get_object_or_404(Producto, id=id)

    # Aquí luego puedes:
    # - agregar al carrito
    # - crear pedido
    # - registrar compra
    # por ahora redirigimos al detalle o al carrito

    return redirect("productos:description_product_client", id=producto.id) 

from django.contrib import messages

@login_required
def toggle_product_status(request, producto_id):
    producto = get_object_or_404(
        Producto,
        id=producto_id,
        tienda__propietario=request.user
    )

    producto.activo = not producto.activo
    producto.save()

    if producto.activo:
        messages.success(request, "Producto habilitado correctamente.")
    else:
        messages.warning(request, "Producto deshabilitado correctamente.")

    return redirect('productos:description_product_seller', producto.id)