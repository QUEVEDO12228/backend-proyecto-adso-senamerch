from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from tiendas.models import Tienda
from .models import Producto, ImagenProducto
from comentarios.models import Comentario
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
# =====================================================
# 🔹 CREAR PRODUCTO - PASO 1
# =====================================================
@login_required
def create_product(request):

    fecha_max = (timezone.now().date() + timedelta(days=14)).isoformat()

    if request.method == "POST":

        nombre = request.POST.get("name", "").strip()
        descripcion = request.POST.get("description", "").strip()
        expiration_date = request.POST.get("expiration_date")
        tipo_producto = request.POST.get("tipo_producto")

        if not all([nombre, descripcion, expiration_date, tipo_producto]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("productos:create_product")

        if tipo_producto not in ["solido", "liquido"]:
            messages.error(request, "Tipo de producto inválido.")
            return redirect("productos:create_product")

        try:
            fecha = datetime.strptime(expiration_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Fecha inválida.")
            return redirect("productos:create_product")

        hoy = timezone.now().date()
        limite = hoy + timedelta(days=14)

        if fecha < hoy:
            messages.error(request, "La fecha no puede ser anterior a hoy.")
            return redirect("productos:create_product")

        if fecha > limite:
            messages.error(request, "La fecha no puede superar 2 semanas desde hoy.")
            return redirect("productos:create_product")

        request.session["product_data"] = {
            "nombre": nombre,
            "descripcion": descripcion,
            "expiration_date": expiration_date,
            "tipo_producto": tipo_producto,
        }

        return redirect("productos:create_product_step2")

    return render(request, "productos/create_product.html", {
        "fecha_max": fecha_max
    })
# =====================================================
# 🔹 PASO 2
# =====================================================
@login_required
def create_product_step2(request):

    product_data = request.session.get("product_data")
    if not product_data:
        return redirect("productos:create_product")

    tipo_producto = product_data.get("tipo_producto")

    categorias_solido = [
        ("verduras", "Verduras"),
        ("frutas", "Frutas"),
        ("granos", "Granos"),
        ("lacteos", "Lácteos"),
    ]

    categorias_liquido = [
        ("lacteos", "Lácteos"),
    ]

    categorias = categorias_liquido if tipo_producto == "liquido" else categorias_solido

    if request.method == "POST":

        categoria = request.POST.get("categoria")
        unidad = request.POST.get("unit")
        precio = request.POST.get("price")
        descuento = request.POST.get("discount") or 0

        if not all([categoria, unidad, precio]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("productos:create_product_step2")

        valores_validos = [c[0] for c in categorias]
        if categoria not in valores_validos:
            messages.error(request, "Categoría inválida para el tipo seleccionado.")
            return redirect("productos:create_product_step2")

        unidades_liquido = ["litro","mililitro","centilitro","decilitro","decalitro","hectolitro","kilolitro"]
        unidades_solido = ["tonelada","kg","g","mg","Uni"]

        if tipo_producto == "liquido" and unidad not in unidades_liquido:
            messages.error(request, "Unidad inválida para líquido.")
            return redirect("productos:create_product_step2")

        if tipo_producto == "solido" and unidad not in unidades_solido:
            messages.error(request, "Unidad inválida para sólido.")
            return redirect("productos:create_product_step2")

        try:
            precio = float(precio)
            descuento = float(descuento)
        except ValueError:
            messages.error(request, "Precio o descuento inválido.")
            return redirect("productos:create_product_step2")

        if precio <= 0:
            messages.error(request, "El precio debe ser mayor que 0.")
            return redirect("productos:create_product_step2")

        if descuento < 0 or descuento > 100:
            messages.error(request, "El descuento debe estar entre 0 y 100.")
            return redirect("productos:create_product_step2")

        product_data.update({
            "categoria": categoria,
            "unidad": unidad,
            "precio": precio,
            "descuento": descuento,
        })

        request.session["product_data"] = product_data

        return redirect("productos:create_product_step3")

    return render(request, "productos/create_product2.html", {
        "tipo_producto": tipo_producto,
        "categorias": categorias
    })

# =====================================================
# 🔹 PASO 3 (INCLUYE STOCK)
# =====================================================
@login_required
def create_product_step3(request):

    product_data = request.session.get("product_data")
    if not product_data:
        return redirect("productos:create_product")

    unidad = product_data.get("unidad")  # 🔥 AQUÍ

    if request.method == "POST":

        metodo_pago = request.POST.get("payment_method")
        tipo_envio = request.POST.get("shipping_type")
        stock = request.POST.get("stock")

        if not all([metodo_pago, tipo_envio, stock]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("productos:create_product_step3")

        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Stock inválido.")
            return redirect("productos:create_product_step3")

        product_data.update({
            "metodo_pago": metodo_pago,
            "tipo_envio": tipo_envio,
            "stock": stock,
        })

        request.session["product_data"] = product_data

        return redirect("productos:create_product_step4")

    # 🔥 ENVIAMOS UNIDAD AL TEMPLATE
    return render(request, "productos/create_product3.html", {
        "unidad": unidad
    })
# =====================================================
# 🔹 PASO 4 - CREACIÓN FINAL
# =====================================================
from tiendas.models import Tienda
from .models import Producto, ImagenProducto


@login_required
def create_product_step4(request):

    product_data = request.session.get("product_data")
    if not product_data:
        return redirect("productos:create_product")

    if request.method == "POST":

        tienda = Tienda.objects.filter(propietario=request.user).first()
        if not tienda:
            messages.error(request, "Debes crear una tienda primero.")
            return redirect("tiendas:create_store")

        producto = Producto.objects.create(
            tienda=tienda,
            nombre=product_data.get("nombre"),
            descripcion=product_data.get("descripcion"),
            precio=product_data.get("precio"),
            categoria=product_data.get("categoria"),
            unidad_medida=product_data.get("unidad"),
            tipo_producto=product_data.get("tipo_producto"),
            descuento=product_data.get("descuento"),
            fecha_caducidad=product_data.get("expiration_date"),
            metodo_pago=product_data.get("metodo_pago"),
            tipo_envio=product_data.get("tipo_envio"),
            stock=product_data.get("stock"),
        )

        imagen_subida = False

        for i in range(1, 7):
            imagen = request.FILES.get(f"image{i}")
            if imagen:
                ImagenProducto.objects.create(producto=producto, imagen=imagen)
                imagen_subida = True

        if not imagen_subida:
            producto.delete()
            messages.error(request, "Debes subir al menos una imagen.")
            return redirect("productos:create_product_step4")

        request.session.pop("product_data", None)

        messages.success(request, "Producto creado correctamente.")
        return redirect("tiendas:seller_catalog")

    return render(request, "productos/create_product4.html")

# =====================================================
# 🔹 EDITAR PRODUCTO - PASO 1
# =====================================================
@login_required
def edit_product_seller(request, id):

    producto = get_object_or_404(
        Producto,
        id=id,
        tienda__propietario=request.user
    )

    fecha_max = (timezone.now().date() + timedelta(days=14)).isoformat()

    if request.method == "POST":

        nombre = request.POST.get("name")
        descripcion = request.POST.get("description")
        expiration_date = request.POST.get("expiration_date")
        tipo_producto = request.POST.get("tipo_producto")

        if not all([nombre, descripcion, expiration_date, tipo_producto]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("productos:edit_product_seller", id=id)

        # 🔥 Validación fecha máximo 2 semanas
        fecha = datetime.strptime(expiration_date, "%Y-%m-%d").date()
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=14)

        if fecha > limite:
            messages.error(request, "La fecha no puede superar 2 semanas desde hoy.")
            return redirect("productos:edit_product_seller", id=id)

        request.session["edit_product_data"] = {
            "nombre": nombre,
            "descripcion": descripcion,
            "fecha_caducidad": expiration_date,
            "tipo_producto": tipo_producto,
        }

        return redirect("productos:edit_product_step2", id=id)

    return render(request, "productos/edit_product_seller.html", {
        "producto": producto,
        "fecha_max": fecha_max
    })


# =====================================================
# 🔹 PASO 2 EDITAR
# =====================================================
@login_required
def edit_product_step2(request, id):

    producto = get_object_or_404(
        Producto,
        id=id,
        tienda__propietario=request.user
    )

    if request.method == "POST":

        categoria = request.POST.get("categoria")
        unidad = request.POST.get("unit")
        precio = request.POST.get("price")
        descuento = request.POST.get("discount")

        if not all([categoria, unidad, precio]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("productos:edit_product_step2", id=id)

        data = request.session.get("edit_product_data", {})
        tipo = data.get("tipo_producto")

        # 🔥 VALIDACIÓN UNIDAD SEGÚN TIPO
        unidades_liquido = ["litro","mililitro","centilitro","decilitro","decalitro","hectolitro","kilolitro"]
        unidades_solido = ["tonelada","kg","g","mg"]

        if tipo == "liquido" and unidad not in unidades_liquido:
            messages.error(request, "Unidad inválida para producto líquido.")
            return redirect("productos:edit_product_step2", id=id)

        if tipo == "solido" and unidad not in unidades_solido:
            messages.error(request, "Unidad inválida para producto sólido.")
            return redirect("productos:edit_product_step2", id=id)

        data.update({
            "categoria": categoria,
            "unidad": unidad,
            "precio": precio,
            "descuento": descuento or 0,
        })

        request.session["edit_product_data"] = data

        return redirect("productos:edit_product_step3", id=id)

    return render(request, "productos/edit_product_seller2.html", {
        "producto": producto
    })

# =====================================================
# 🔹 PASO 3 EDITAR (INCLUYE STOCK)
# =====================================================
@login_required
def edit_product_step3(request, id):

    producto = get_object_or_404(
        Producto,
        id=id,
        tienda__propietario=request.user
    )

    # 🔥 Obtén la unidad desde la sesión si existe
    edit_data = request.session.get("edit_product_data", {})
    unidad = edit_data.get("unidad", producto.unidad_medida)

    if request.method == "POST":

        tipo_envio = request.POST.get("shipping_type")
        metodo_pago = request.POST.get("payment_method")
        stock = request.POST.get("stock")

        if not all([tipo_envio, metodo_pago, stock]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("productos:edit_product_step3", id=id)

        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError
        except ValueError:
            messages.error(request, "El stock debe ser un número válido mayor o igual a 0.")
            return redirect("productos:edit_product_step3", id=id)

        # 🔥 Mantén la unidad si la cambiaste en pasos anteriores
        unidad = edit_data.get("unidad", producto.unidad_medida)

        edit_data.update({
            "tipo_envio": tipo_envio,
            "metodo_pago": metodo_pago,
            "stock": stock,
            "unidad": unidad,  # 🔥 Asegúrate de guardar la unidad también
        })

        request.session["edit_product_data"] = edit_data

        return redirect("productos:edit_product_step4", id=id)

    return render(request, "productos/edit_product_seller3.html", {
        "producto": producto,
        "unidad": unidad  # 🔥 PASAR AL TEMPLATE
    })
# =====================================================
# 🔹 PASO 4 EDITAR - GUARDAR
# =====================================================
@login_required
def edit_product_step4(request, id):

    producto = get_object_or_404(
        Producto,
        id=id,
        tienda__propietario=request.user
    )

    imagenes = producto.imagenes.order_by("id")

    if request.method == "POST":

        data = request.session.get("edit_product_data")

        if not data:
            return redirect("productos:edit_product_seller", id=id)

        # 🔥 VALIDACIÓN FINAL CRÍTICA
        tipo = data.get("tipo_producto")
        unidad = data.get("unidad")
        stock = data.get("stock")

        unidades_liquido = ["litro","mililitro","centilitro","decilitro","decalitro","hectolitro","kilolitro"]
        unidades_solido = ["tonelada","kg","g","mg"]

        if tipo == "liquido" and unidad not in unidades_liquido:
            messages.error(request, "Error de validación en unidad.")
            return redirect("productos:edit_product_seller", id=id)

        if tipo == "solido" and unidad not in unidades_solido:
            messages.error(request, "Error de validación en unidad.")
            return redirect("productos:edit_product_seller", id=id)

        if int(stock) < 0:
            messages.error(request, "Stock inválido.")
            return redirect("productos:edit_product_seller", id=id)

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
        producto.stock = int(data.get("stock") or 0)  # 🔥 NUEVO

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

        messages.success(request, "Producto actualizado correctamente.")

        return redirect("tiendas:seller_catalog")

    return render(request, "productos/edit_product_seller4.html", {
        "producto": producto,
        "imagenes": imagenes
    })


# =====================================================
# 🔹 DESCRIPCIÓN VENDEDOR
# =====================================================
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
            return redirect("productos:description_product_seller", id=id)

    comentarios = producto.comentarios.order_by("-creado_en")

    return render(request, "productos/description_product_seller.html", {
        "producto": producto,
        "comentarios": comentarios
    })
# =====================================================
# 🔹 DESCRIPCIÓN CLIENTE
# =====================================================
def description_product_client(request, id):

    producto = get_object_or_404(Producto, id=id)

    return render(request, "usuarios/description_product_client.html", {
        "producto": producto
    })

# =====================================================
# 🔹 ACTIVAR / DESACTIVAR PRODUCTO
# =====================================================
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

    return redirect("productos:description_product_seller", producto.id)

def buy_product(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'usuarios/buy_product.html', {
        'producto': producto
    })

def lista_productos(request):
    productos = Producto.objects.filter(activo=True)
    return render(request, 'productos/lista_productos.html', {'productos': productos})

def buscar(request):

    query = request.GET.get('q')

    productos = []
    tiendas = []

    if query:

        productos = Producto.objects.filter(
            Q(nombre__icontains=query) |
            Q(categoria__icontains=query) |
            Q(descripcion__icontains=query),
            activo=True
        )

        tiendas = Tienda.objects.filter(
            Q(nombre__icontains=query) |
            Q(categoria__icontains=query),
            activa=True
        )

    context = {
        "query": query,
        "productos": productos,
        "tiendas": tiendas
    }

    return render(request, "productos/busqueda.html", context)



from django.http import JsonResponse
import difflib

def sugerencias_busqueda(request):

    query = request.GET.get("q", "").lower()

    productos_db = Producto.objects.filter(activo=True)

    nombres_productos = [p.nombre.lower() for p in productos_db]

    coincidencias = difflib.get_close_matches(
        query,
        nombres_productos,
        n=5,
        cutoff=0.4
    )

    productos = []

    for producto in productos_db:

        if (
            query in producto.nombre.lower()
            or producto.nombre.lower() in coincidencias
        ):

            imagen_url = ""

            imagen = producto.imagenes.first()
            if imagen:
                imagen_url = imagen.imagen.url

            productos.append({
                "nombre": producto.nombre,
                "precio": producto.precio,
                "categoria": producto.categoria,
                "imagen": imagen_url
            })

    productos = productos[:5]

    tiendas = list(
        Tienda.objects.filter(
            nombre__icontains=query,
            activa=True
        ).values("nombre")[:5]
    )

    return JsonResponse({
        "productos": productos,
        "tiendas": tiendas
    })