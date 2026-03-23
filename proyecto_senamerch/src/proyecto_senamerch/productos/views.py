from django.shortcuts import render, redirect, get_object_or_404  # Funciones para manejar vistas y redirecciones
from django.contrib.auth.decorators import login_required  # Requiere que el usuario esté autenticado
from django.contrib import messages  # Sistema de mensajes de Django
from datetime import datetime  # Manejo de fechas
from tiendas.models import Tienda  # Modelo de tiendas
from .models import Producto, ImagenProducto  # Modelos de producto e imágenes
from comentarios.models import Comentario  # Modelo de comentarios
from django.db.models import Q  # Permite consultas complejas en ORM
from datetime import datetime, timedelta  # Manejo de fechas y diferencias
from django.utils import timezone  # Manejo de zona horaria
from django.http import JsonResponse  # Respuestas JSON para APIs o AJAX
from tiendas.models import Tienda
from .models import Producto, ImagenProducto
from productos.models import Calificacion

# =====================================================
# 🔹 CREAR PRODUCTO - PASO 1
# =====================================================
@login_required
def create_product(request):
    # Fecha máxima permitida para caducidad (14 días desde hoy)
    fecha_max = (timezone.now().date() + timedelta(days=14)).isoformat()
    if request.method == "POST":
        # Obtener datos del formulario
        nombre = request.POST.get("name", "").strip()
        descripcion = request.POST.get("description", "").strip()
        expiration_date = request.POST.get("expiration_date")
        tipo_producto = request.POST.get("tipo_producto")
        # Validar campos obligatorios
        if not all([nombre, descripcion, expiration_date, tipo_producto]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("productos:create_product")
        # Validar tipo de producto
        if tipo_producto not in ["solido", "liquido"]:
            messages.error(request, "Tipo de producto inválido.")
            return redirect("productos:create_product")
        # Convertir fecha enviada a objeto date
        try:
            fecha = datetime.strptime(expiration_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Fecha inválida.")
            return redirect("productos:create_product")
        # Validar rango de fecha permitido
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=14)
        if fecha < hoy:
            messages.error(request, "La fecha no puede ser anterior a hoy.")
            return redirect("productos:create_product")
        if fecha > limite:
            messages.error(request, "La fecha no puede superar 2 semanas desde hoy.")
            return redirect("productos:create_product")
        # Guardar datos en sesión para pasos siguientes
        request.session["product_data"] = {
            "nombre": nombre,
            "descripcion": descripcion,
            "expiration_date": expiration_date,
            "tipo_producto": tipo_producto,
        }
        # Redirigir al paso 2
        return redirect("productos:create_product_step2")
    # Renderizar formulario del paso 1
    return render(request, "productos/create_product.html", {
        "fecha_max": fecha_max
    })
# =======================
# 🔹 PASO 2 CREAR TIENDA
# =======================
@login_required
def create_product_step2(request):
    # Recuperar datos del producto desde sesión
    product_data = request.session.get("product_data")
    if not product_data:
        return redirect("productos:create_product")
    tipo_producto = product_data.get("tipo_producto")
    # Categorías permitidas para productos sólidos
    categorias_solido = [
        ("verduras", "Verduras"),
        ("frutas", "Frutas"),
        ("granos", "Granos"),
        ("lacteos", "Lácteos"),
    ]
    # Categorías permitidas para productos líquidos
    categorias_liquido = [
        ("lacteos", "Lácteos"),
    ]
    # Seleccionar categorías según tipo
    categorias = categorias_liquido if tipo_producto == "liquido" else categorias_solido
    if request.method == "POST":
        # Obtener datos del formulario
        categoria = request.POST.get("categoria")
        unidad = request.POST.get("unit")
        precio = request.POST.get("price")
        descuento = request.POST.get("discount") or 0
        # Validar campos obligatorios
        if not all([categoria, unidad, precio]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("productos:create_product_step2")
        # Validar categoría según tipo de producto
        valores_validos = [c[0] for c in categorias]
        if categoria not in valores_validos:
            messages.error(request, "Categoría inválida para el tipo seleccionado.")
            return redirect("productos:create_product_step2")
        # Unidades válidas según tipo de producto
        unidades_liquido = ["litro","mililitro","centilitro","decilitro","decalitro","hectolitro","kilolitro"]
        unidades_solido = ["tonelada","kg","g","mg","Uni"]
        # Validar unidad para líquidos
        if tipo_producto == "liquido" and unidad not in unidades_liquido:
            messages.error(request, "Unidad inválida para líquido.")
            return redirect("productos:create_product_step2")
        # Validar unidad para sólidos
        if tipo_producto == "solido" and unidad not in unidades_solido:
            messages.error(request, "Unidad inválida para sólido.")
            return redirect("productos:create_product_step2")
        # Convertir precio y descuento a números
        try:
            precio = float(precio)
            descuento = float(descuento)
        except ValueError:
            messages.error(request, "Precio o descuento inválido.")
            return redirect("productos:create_product_step2")
        # Validar precio positivo
        if precio <= 0:
            messages.error(request, "El precio debe ser mayor que 0.")
            return redirect("productos:create_product_step2")
        # Validar rango de descuento
        if descuento < 0 or descuento > 100:
            messages.error(request, "El descuento debe estar entre 0 y 100.")
            return redirect("productos:create_product_step2")
        # Actualizar datos del producto en sesión
        product_data.update({
            "categoria": categoria,
            "unidad": unidad,
            "precio": precio,
            "descuento": descuento,
        })
        request.session["product_data"] = product_data
        # Redirigir al paso 3
        return redirect("productos:create_product_step3")
    # Renderizar formulario paso 2
    return render(request, "productos/create_product2.html", {
        "tipo_producto": tipo_producto,
        "categorias": categorias
    })
# =====================================================
# 🔹 PASO 3 (INCLUYE STOCK)
# =====================================================
@login_required
def create_product_step3(request):
    # Obtener datos del producto desde sesión
    product_data = request.session.get("product_data")
    if not product_data:
        return redirect("productos:create_product")
    # Obtener unidad de medida para mostrar en template
    unidad = product_data.get("unidad")
    if request.method == "POST":
        # Obtener datos del formulario
        metodo_pago = request.POST.get("payment_method")
        tipo_envio = request.POST.get("shipping_type")
        stock = request.POST.get("stock")
        # Validar campos obligatorios
        if not all([metodo_pago, tipo_envio, stock]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("productos:create_product_step3")
        # Validar stock como número entero positivo
        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Stock inválido.")
            return redirect("productos:create_product_step3")
        # Guardar datos en sesión
        product_data.update({
            "metodo_pago": metodo_pago,
            "tipo_envio": tipo_envio,
            "stock": stock,
        })
        request.session["product_data"] = product_data
        # Redirigir al paso final
        return redirect("productos:create_product_step4")
    # Renderizar formulario paso 3
    return render(request, "productos/create_product3.html", {
        "unidad": unidad
    })
# =====================================================
# 🔹 PASO 4 - CREACIÓN FINAL
# =====================================================
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

        # ✅ AQUÍ ESTÁ LA CLAVE
        messages.success(request, "Producto creado correctamente.")
        return render(request, "productos/create_product4.html", {
            "redirect_url": "tiendas:seller_catalog"
        })

    return render(request, "productos/create_product4.html")
# =====================================================
# 🔹 EDITAR PRODUCTO - PASO 1
# =====================================================
@login_required
def edit_product_seller(request, id):
    # Obtener producto que pertenece al vendedor
    producto = get_object_or_404(
        Producto,
        id=id,
        tienda__propietario=request.user
    )
    # Fecha máxima permitida (14 días desde hoy)
    fecha_max = (timezone.now().date() + timedelta(days=14)).isoformat()
    if request.method == "POST":
        # Obtener datos del formulario
        nombre = request.POST.get("name")
        descripcion = request.POST.get("description")
        expiration_date = request.POST.get("expiration_date")
        tipo_producto = request.POST.get("tipo_producto")
        # Validar campos obligatorios
        if not all([nombre, descripcion, expiration_date, tipo_producto]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("productos:edit_product_seller", id=id)
        # Convertir fecha enviada
        fecha = datetime.strptime(expiration_date, "%Y-%m-%d").date()
        # Validar rango máximo de fecha
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=14)
        if fecha > limite:
            messages.error(request, "La fecha no puede superar 2 semanas desde hoy.")
            return redirect("productos:edit_product_seller", id=id)
        # Guardar datos en sesión para siguientes pasos
        request.session["edit_product_data"] = {
            "nombre": nombre,
            "descripcion": descripcion,
            "fecha_caducidad": expiration_date,
            "tipo_producto": tipo_producto,
        }
        # Redirigir al paso 2
        return redirect("productos:edit_product_step2", id=id)
    # Renderizar formulario de edición
    return render(request, "productos/edit_product_seller.html", {
        "producto": producto,
        "fecha_max": fecha_max
    })
# =====================================================
# 🔹 PASO 2 EDITAR
# =====================================================
@login_required
def edit_product_step2(request, id):
    # Obtener producto del vendedor
    producto = get_object_or_404(
        Producto,
        id=id,
        tienda__propietario=request.user
    )
    if request.method == "POST":
        # Obtener datos del formulario
        categoria = request.POST.get("categoria")
        unidad = request.POST.get("unit")
        precio = request.POST.get("price")
        descuento = request.POST.get("discount")
        # Validar campos obligatorios
        if not all([categoria, unidad, precio]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("productos:edit_product_step2", id=id)
        # Recuperar datos guardados del paso anterior
        data = request.session.get("edit_product_data", {})
        tipo = data.get("tipo_producto")
        # Unidades válidas según tipo de producto
        unidades_liquido = ["litro","mililitro","centilitro","decilitro","decalitro","hectolitro","kilolitro"]
        unidades_solido = ["tonelada","kg","g","mg"]
        # Validar unidad para producto líquido
        if tipo == "liquido" and unidad not in unidades_liquido:
            messages.error(request, "Unidad inválida para producto líquido.")
            return redirect("productos:edit_product_step2", id=id)
        # Validar unidad para producto sólido
        if tipo == "solido" and unidad not in unidades_solido:
            messages.error(request, "Unidad inválida para producto sólido.")
            return redirect("productos:edit_product_step2", id=id)
        # Actualizar datos del producto en sesión
        data.update({
            "categoria": categoria,
            "unidad": unidad,
            "precio": precio,
            "descuento": descuento or 0,
        })
        request.session["edit_product_data"] = data
        # Redirigir al paso 3
        return redirect("productos:edit_product_step3", id=id)
    # Renderizar formulario paso 2
    return render(request, "productos/edit_product_seller2.html", {
        "producto": producto
    })
# =====================================================
# 🔹 PASO 3 EDITAR (INCLUYE STOCK)
# =====================================================
@login_required
def edit_product_step3(request, id):
    # Obtener producto del vendedor
    producto = get_object_or_404(
        Producto,
        id=id,
        tienda__propietario=request.user
    )
    # Recuperar datos editados desde sesión
    edit_data = request.session.get("edit_product_data", {})
    # Obtener unidad actual o la modificada
    unidad = edit_data.get("unidad", producto.unidad_medida)
    if request.method == "POST":
        # Obtener datos del formulario
        tipo_envio = request.POST.get("shipping_type")
        metodo_pago = request.POST.get("payment_method")
        stock = request.POST.get("stock")
        # Validar campos obligatorios
        if not all([tipo_envio, metodo_pago, stock]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("productos:edit_product_step3", id=id)
        # Validar stock como número entero
        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError
        except ValueError:
            messages.error(request, "El stock debe ser un número válido mayor o igual a 0.")
            return redirect("productos:edit_product_step3", id=id)
        # Mantener unidad si fue modificada en pasos anteriores
        unidad = edit_data.get("unidad", producto.unidad_medida)
        # Actualizar datos del producto en sesión
        edit_data.update({
            "tipo_envio": tipo_envio,
            "metodo_pago": metodo_pago,
            "stock": stock,
            "unidad": unidad,
        })
        request.session["edit_product_data"] = edit_data
        # Redirigir al paso final
        return redirect("productos:edit_product_step4", id=id)
    # Renderizar formulario paso 3
    return render(request, "productos/edit_product_seller3.html", {
        "producto": producto,
        "unidad": unidad
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
        producto.stock = int(data.get("stock") or 0)

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

        # ALERTA
        messages.success(request, "Cambios guardados correctamente.")

        return render(request, "productos/edit_product_seller4.html", {
            "producto": producto,
            "imagenes": imagenes,
            "redirect_url": "tiendas:seller_catalog"
        })

    return render(request, "productos/edit_product_seller4.html", {
        "producto": producto,
        "imagenes": imagenes
    })
# =====================================================
# 🔹 DESCRIPCIÓN VENDEDOR
# ===================================================== 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from productos.models import Producto, Comentario

@login_required
def description_product_seller(request, id):
    # Obtener producto
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

    # Obtener comentarios usando el related_name único
    comentarios = producto.comentarios_producto.order_by("-creado_en")

    # Renderizar la plantilla
    return render(request, "productos/description_product_seller.html", {
        "producto": producto,
        "comentarios": comentarios
    })
# =====================================================
# 🔹 DESCRIPCIÓN CLIENTE
# =====================================================
from django.shortcuts import render, get_object_or_404
from productos.models import Producto, Calificacion
from tiendas.models import Tienda

def description_product_client(request, id):
    producto = get_object_or_404(Producto, id=id)

    # Calificación del usuario
    user_rating = 0
    if request.user.is_authenticated:
        calificacion = Calificacion.objects.filter(
            producto=producto,
            usuario=request.user
        ).first()
        if calificacion:
            user_rating = calificacion.puntuacion

    # 🔹 Otros productos de la misma tienda, excluyendo el actual
    otros_productos = producto.tienda.productos.exclude(id=producto.id)[:1]  # solo 1 producto más

    # Comentarios del producto
    comentarios = producto.calificaciones.select_related("usuario").all()

    # 🔥 Detectar si es vendedor
    es_vendedor = False
    if request.user.is_authenticated:
        es_vendedor = Tienda.objects.filter(propietario=request.user).exists()

    return render(request, "usuarios/description_product_client.html", {
        "producto": producto,
        "otros_productos": otros_productos,
        "comentarios": comentarios,
        "user_rating": user_rating,
        "es_vendedor": es_vendedor
    })
# =====================================================
# 🔹 ACTIVAR / DESACTIVAR PRODUCTO
# =====================================================
@login_required
def toggle_product_status(request, producto_id):
    # Obtener producto del vendedor
    producto = get_object_or_404(
        Producto,
        id=producto_id,
        tienda__propietario=request.user
    )
    # Cambiar estado activo/inactivo
    producto.activo = not producto.activo
    producto.save()
    # Mostrar mensaje según estado
    if producto.activo:
        messages.success(request, "Producto habilitado correctamente.")
    else:
        messages.warning(request, "Producto deshabilitado correctamente.")
    # Redirigir a la descripción del producto
    return redirect("productos:description_product_seller", producto.id)
# =====================================================
# 🔹 COMPRA DE PRODUCTO
# =====================================================
def buy_product(request, producto_id):
    # Obtener producto
    producto = get_object_or_404(Producto, id=producto_id)
    # Renderizar vista de compra
    return render(request, 'usuarios/buy_product.html', {
        'producto': producto
    })
# =====================================================
# 🔹 LISTA DE PRODUCTOS
# =====================================================
def lista_productos(request):
    # Obtener productos activos
    productos = Producto.objects.filter(activo=True)
    # Renderizar lista de productos
    return render(request, 'productos/lista_productos.html', {
        'productos': productos
    })
# =====================================================
# 🔹 BUSCADOR GENERAL
# =====================================================
def buscar(request):
    # Obtener consulta de búsqueda
    query = request.GET.get('q')
    productos = []
    tiendas = []
    if query:
        # Buscar productos por nombre, categoría o descripción
        productos = Producto.objects.filter(
            Q(nombre__icontains=query) |
            Q(categoria__icontains=query) |
            Q(descripcion__icontains=query),
            activo=True
        )
        # Buscar tiendas por nombre o categoría
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
    # Renderizar resultados de búsqueda
    return render(request, "productos/busqueda.html", context)
# =====================================================
# 🔹 SUGERENCIAS DE BÚSQUEDA (AJAX)
# =====================================================
from django.http import JsonResponse
import difflib
def sugerencias_busqueda(request):
    # Obtener texto de búsqueda
    query = request.GET.get("q", "").lower()
    # Obtener productos activos
    productos_db = Producto.objects.filter(activo=True)
    # Lista de nombres de productos
    nombres_productos = [p.nombre.lower() for p in productos_db]
    # Buscar coincidencias aproximadas
    coincidencias = difflib.get_close_matches(
        query,
        nombres_productos,
        n=5,
        cutoff=0.4
    )
    productos = []
    # Construir lista de sugerencias
    for producto in productos_db:
        if (
            query in producto.nombre.lower()
            or producto.nombre.lower() in coincidencias
        ):
            imagen_url = ""
            # Obtener imagen principal si existe
            imagen = producto.imagenes.first()
            if imagen:
                imagen_url = imagen.imagen.url
            productos.append({
                "nombre": producto.nombre,
                "precio": producto.precio,
                "categoria": producto.categoria,
                "imagen": imagen_url
            })
    # Limitar resultados a 5
    productos = productos[:5]
    # Obtener sugerencias de tiendas
    tiendas = list(
        Tienda.objects.filter(
            nombre__icontains=query,
            activa=True
        ).values("nombre")[:5]
    )
    # Retornar resultados en formato JSON
    return JsonResponse({
        "productos": productos,
        "tiendas": tiendas
    })

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from productos.models import Producto, Calificacion
import json

@login_required
@csrf_exempt
def calificar_producto(request):
    if request.method == "POST":
        data = json.loads(request.body)
        producto_id = data.get("producto_id")
        puntuacion = data.get("puntuacion")

        producto = get_object_or_404(Producto, id=producto_id)

        calificacion, _ = Calificacion.objects.update_or_create(
            producto=producto,
            usuario=request.user,
            defaults={"puntuacion": puntuacion}
        )

        return JsonResponse({"success": True, "puntuacion": calificacion.puntuacion})

    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)