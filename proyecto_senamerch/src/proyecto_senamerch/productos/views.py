from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from tiendas.models import Tienda
from .models import Producto, ImagenProducto
from datetime import datetime

# 🔹 PASO 1
@login_required
def create_product(request):
    if request.method == "POST":

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