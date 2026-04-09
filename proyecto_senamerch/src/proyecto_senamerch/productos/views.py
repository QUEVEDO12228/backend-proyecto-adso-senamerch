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
# CREAR PRODUCTO - PASO 1
# =====================================================
@login_required
def create_product(request):
    fecha_max = (timezone.now().date() + timedelta(days=14)).isoformat()
    
    # Si hay datos guardados en sesión, los usamos para rellenar el formulario
    session_data = request.session.get("product_data", {})
    
    if request.method == "POST":
        nombre = request.POST.get("name", "").strip()
        descripcion = request.POST.get("description", "").strip()
        expiration_date = request.POST.get("expiration_date")
        tipo_producto = request.POST.get("tipo_producto")
        
        if not all([nombre, descripcion, expiration_date, tipo_producto]):
            messages.error(request, "Todos los campos son obligatorios.")
            # Renderizamos con los datos ingresados para que no se pierdan
            return render(request, "productos/create_product.html", {
                "fecha_max": fecha_max,
                "form_data": {
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "expiration_date": expiration_date,
                    "tipo_producto": tipo_producto,
                }
            })
        
        if tipo_producto not in ["solido", "liquido"]:
            messages.error(request, "Tipo de producto inválido.")
            return render(request, "productos/create_product.html", {
                "fecha_max": fecha_max,
                "form_data": session_data
            })
        
        try:
            fecha = datetime.strptime(expiration_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Fecha inválida.")
            return render(request, "productos/create_product.html", {
                "fecha_max": fecha_max,
                "form_data": session_data
            })
        
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=14)
        if fecha < hoy or fecha > limite:
            messages.error(request, "La fecha debe estar entre hoy y dos semanas.")
            return render(request, "productos/create_product.html", {
                "fecha_max": fecha_max,
                "form_data": session_data
            })
        
        # Guardar datos en sesión
        request.session["product_data"] = {
            "nombre": nombre,
            "descripcion": descripcion,
            "expiration_date": expiration_date,
            "tipo_producto": tipo_producto,
        }
        
        return redirect("productos:create_product_step2")
    
    # GET: precargar datos de sesión si existen
    return render(request, "productos/create_product.html", {
        "fecha_max": fecha_max,
        "form_data": session_data
    })
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal

@login_required
def create_product_step2(request):
    # Recuperar datos del producto desde sesión
    product_data = request.session.get("product_data", {})

    if not product_data:
        return redirect("productos:create_product")

    tipo_producto = product_data.get("tipo_producto")

    # Categorías
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

    # Unidades
    unidades_liquido = ["litro","mililitro","centilitro","decilitro","decalitro","hectolitro","kilolitro"]
    unidades_solido = ["tonelada","kg","g","mg","Uni"]
    unidades = unidades_liquido if tipo_producto == "liquido" else unidades_solido

    form_errors = {}

    if request.method == "POST":
        # Obtener datos del formulario
        categoria = request.POST.get("categoria")
        unidad = request.POST.get("unit")
        precio = request.POST.get("price")
        descuento = request.POST.get("discount") or 0

        # Guardar temporalmente en sesión para mostrar de nuevo en el template
        product_data["categoria"] = categoria
        product_data["unidad"] = unidad
        product_data["precio"] = precio
        product_data["descuento"] = descuento

        # Validaciones
        if not all([categoria, unidad, precio]):
            messages.error(request, "Todos los campos obligatorios deben ser completados.")

        valores_validos = [c[0] for c in categorias]
        if categoria not in valores_validos:
            form_errors['categoria'] = "Categoría inválida."

        if tipo_producto == "liquido" and unidad not in unidades_liquido:
            form_errors['unidad'] = "Unidad inválida para líquido."
        if tipo_producto == "solido" and unidad not in unidades_solido:
            form_errors['unidad'] = "Unidad inválida para sólido."

        # Convertir precio y descuento
        try:
            precio_decimal = Decimal(precio)
            if precio_decimal <= 0:
                form_errors['precio'] = "El precio debe ser mayor que 0."
        except:
            form_errors['precio'] = "El precio debe ser un número válido."

        try:
            descuento_int = int(descuento)
            if descuento_int < 0 or descuento_int > 100:
                form_errors['descuento'] = "El descuento debe estar entre 0 y 100."
        except:
            form_errors['descuento'] = "El descuento debe ser un número entero válido."

        if form_errors:
            # Guardar la sesión para mantener valores ingresados
            request.session["product_data"] = product_data
            return render(request, "productos/create_product2.html", {
                "tipo_producto": tipo_producto,
                "categorias": categorias,
                "unidades": unidades,
                "product_data": product_data,
                "form_errors": form_errors
            })

        # Guardar ya convertidos correctamente
        product_data.update({
            "precio": str(precio_decimal),   # guardamos como str para mostrar
            "descuento": descuento_int
        })
        request.session["product_data"] = product_data

        return redirect("productos:create_product_step3")

    return render(request, "productos/create_product2.html", {
        "tipo_producto": tipo_producto,
        "categorias": categorias,
        "unidades": unidades,
        "product_data": product_data,
        "form_errors": form_errors
    })
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def create_product_step3(request):
    # Obtener datos del producto desde sesión
    product_data = request.session.get("product_data", {})
    if not product_data:
        return redirect("productos:create_product")

    unidad = product_data.get("unidad")
    form_errors = {}

    if request.method == "POST":
        # Obtener datos del formulario
        metodo_pago = request.POST.get("payment_method")
        tipo_envio = request.POST.get("shipping_type")
        stock = request.POST.get("stock")

        # Guardar temporalmente en session para mostrar en template
        product_data["metodo_pago"] = metodo_pago
        product_data["tipo_envio"] = tipo_envio
        product_data["stock"] = stock

        # Validaciones
        if not metodo_pago:
            form_errors['metodo_pago'] = "Debe seleccionar un método de pago."
        if not tipo_envio:
            form_errors['tipo_envio'] = "Debe seleccionar un tipo de envío."

        try:
            stock_int = int(stock)
            if stock_int < 0:
                form_errors['stock'] = "El stock debe ser mayor o igual a 0."
        except:
            form_errors['stock'] = "Stock inválido, ingrese un número entero."

        # Si hay errores, renderizamos el template con errores
        if form_errors:
            return render(request, "productos/create_product3.html", {
                "unidad": unidad,
                "product_data": product_data,
                "form_errors": form_errors
            })

        # Guardar valores correctos en la sesión
        product_data.update({
            "metodo_pago": metodo_pago,
            "tipo_envio": tipo_envio,
            "stock": stock_int
        })
        request.session["product_data"] = product_data

        # Redirigir al paso final
        return redirect("productos:create_product_step4")

    # GET: renderizar formulario
    return render(request, "productos/create_product3.html", {
        "unidad": unidad,
        "product_data": product_data,
        "form_errors": form_errors
    })
# =====================================================
# PASO 4 - CREACIÓN FINAL
# =====================================================
@login_required
def create_product_step4(request):
    product_data = request.session.get("product_data")
    if not product_data:
        return redirect("productos:create_product")

    form_errors = {}

    if request.method == "POST":

        tienda = Tienda.objects.filter(propietario=request.user).first()
        if not tienda:
            messages.error(request, "Debes crear una tienda primero.")
            return redirect("tiendas:create_store")

        # Crear producto primero
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
        uploaded_images = {}

        # Guardar cada imagen subida
        for i in range(1, 7):
            imagen = request.FILES.get(f"image{i}")
            if imagen:
                ImagenProducto.objects.create(producto=producto, imagen=imagen)
                imagen_subida = True
                uploaded_images[str(i)] = imagen
            else:
                uploaded_images[str(i)] = None

        # Validación: al menos una imagen
        if not imagen_subida:
            producto.delete()
            form_errors["images"] = "Debes subir al menos una imagen."
            messages.error(request, form_errors["images"])
            return render(request, "productos/create_product4.html", {
                "form_errors": form_errors,
            })

        # Todo OK: limpiar sesión y redirigir
        request.session.pop("product_data", None)
        messages.success(request, "Producto creado correctamente.")
        return render(request, "productos/create_product4.html", {
            "redirect_url": "tiendas:seller_catalog"
        })

    # GET: renderizar formulario
    return render(request, "productos/create_product4.html", {
        "form_errors": form_errors,
    })
# =====================================================
# EDITAR PRODUCTO - PASO 1
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
# PASO 2 EDITAR
# =====================================================
@login_required
def edit_product_step2(request, id):
    # Obtener el producto del vendedor
    producto = get_object_or_404(
        Producto,
        id=id,
        tienda__propietario=request.user
    )

    # Obtener datos guardados en sesión o inicializar con los actuales
    data = request.session.get("edit_product_data", {
        "categoria": producto.categoria,
        "unidad": producto.unidad_medida,
        "precio": str(producto.precio),  # Asegurarse de pasar como string
        "descuento": producto.descuento or 0,
        "tipo_producto": producto.tipo_producto,
    })

    # Si el método es POST, se procesan los datos del formulario
    if request.method == "POST":
        categoria = request.POST.get("categoria")
        unidad = request.POST.get("unit")
        precio = request.POST.get("price")
        descuento = request.POST.get("discount") or "0"  # default a "0" si no viene

        # Validación de campos obligatorios
        if not all([categoria, unidad, precio]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("productos:edit_product_step2", id=id)

        # Validar que el precio sea un número decimal válido
        try:
            precio_decimal = Decimal(precio)
            if precio_decimal <= 0:
                raise ValueError
        except:
            messages.error(request, "El precio debe ser un número positivo.")
            return redirect("productos:edit_product_step2", id=id)

        # Validar que el descuento sea un número entero entre 0 y 100
        try:
            descuento_int = int(descuento)
            if descuento_int < 0 or descuento_int > 100:
                raise ValueError
        except:
            messages.error(request, "El descuento debe ser un número entero entre 0 y 100.")
            return redirect("productos:edit_product_step2", id=id)

        # Validar unidad según el tipo de producto
        tipo = data.get("tipo_producto")
        unidades_liquido = ["litro", "mililitro", "centilitro", "decilitro", "decalitro", "hectolitro", "kilolitro"]
        unidades_solido = ["tonelada", "kg", "g", "mg", "uni"]

        if tipo == "liquido" and unidad not in unidades_liquido:
            messages.error(request, "Unidad inválida para producto líquido.")
            return redirect("productos:edit_product_step2", id=id)
        if tipo == "solido" and unidad not in unidades_solido:
            messages.error(request, "Unidad inválida para producto sólido.")
            return redirect("productos:edit_product_step2", id=id)

        # Guardar todo en la sesión para mantener el flujo
        data.update({
            "categoria": categoria,
            "unidad": unidad,
            "precio": str(precio_decimal),  # Guardamos como string para el formulario
            "descuento": descuento_int,
        })
        request.session["edit_product_data"] = data

        # Actualizar el producto en la base de datos
        producto.categoria = categoria
        producto.unidad_medida = unidad
        producto.precio = precio_decimal
        producto.descuento = descuento_int
        producto.save()

        # Redirigir al siguiente paso
        return redirect("productos:edit_product_step3", id=id)

    # Renderizar formulario con valores de sesión si existen
    return render(request, "productos/edit_product_seller2.html", {
        "producto": producto,
        "data": data,  # Pasar los datos a la plantilla
    })
# =====================================================
# PASO 3 EDITAR (INCLUYE STOCK)
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
# PASO 4 EDITAR - GUARDAR
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
# DESCRIPCIÓN VENDEDOR
# ===================================================== 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from productos.models import Producto, Comentario

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Producto, Comentario

@login_required
def description_product_seller(request, id):
    producto = get_object_or_404(Producto, id=id)

    # 🚨 BLOQUEO TOTAL SI PRODUCTO INACTIVO
    if not producto.activo:
        if request.method == "POST":
            return redirect("productos:description_product_seller", id=id)

    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()  # ✅ CORREGIDO

        if texto:
            Comentario.objects.create(
                producto=producto,
                usuario=request.user,
                texto=texto
            )
            return redirect("productos:description_product_seller", id=id)

    comentarios = producto.comentarios_producto.order_by("-creado_en")

    return render(request, "productos/description_product_seller.html", {
        "producto": producto,
        "comentarios": comentarios
    })
# =====================================================
# DESCRIPCIÓN CLIENTE
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

    # Otros productos de la misma tienda, excluyendo el actual
    otros_productos = producto.tienda.productos.exclude(id=producto.id)[:1]  # solo 1 producto más

    # Comentarios del producto
    comentarios = producto.calificaciones.select_related("usuario").all()

    # Detectar si es vendedor
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
# ACTIVAR / DESACTIVAR PRODUCTO
# =====================================================
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Producto

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

@require_POST
@login_required
def toggle_product_status(request, producto_id):
    producto = get_object_or_404(
        Producto,
        id=producto_id,
        tienda__propietario=request.user
    )

    # 🔴 SI ESTÁ INACTIVO → INTENTAR ACTIVAR
    if not producto.activo:

        # 🚨 VALIDACIÓN: NO ACTIVAR SIN STOCK
        if producto.stock == 0:
            messages.error(request, "No puedes habilitar un producto sin stock.")
            return redirect("productos:description_product_seller", producto.id)

        producto.activo = True
        messages.success(request, "Producto habilitado correctamente.")

    # 🟢 SI ESTÁ ACTIVO → DESHABILITAR
    else:
        producto.activo = False
        messages.warning(request, "Producto deshabilitado correctamente.")

    producto.save()

    # 🔁 REDIRECCIÓN FINAL (como pediste)
    return redirect("productos:description_product_seller", producto.id)
# =====================================================
# COMPRA DE PRODUCTO
# =====================================================
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from productos.models import Producto
from tiendas.models import Tienda

@login_required
def buy_product(request, producto_id):
    # Obtener producto
    producto = get_object_or_404(Producto, id=producto_id)

    # Variables para el navbar
    es_vendedor = False
    tienda_inactiva = False

    if request.user.is_authenticated:
        # Buscar la tienda del usuario
        tienda = Tienda.objects.filter(propietario=request.user).first()
        if tienda:
            if tienda.activo:
                es_vendedor = True
            else:
                tienda_inactiva = True

    # VALIDAR STOCK: si el producto no tiene stock, redirigir al listado y mostrar mensaje
    if producto.stock <= 0:
        messages.error(request, f"Lo sentimos, {producto.nombre} no tiene stock disponible.")
        return redirect('productos:lista_productos')

    # Renderizar vista de compra pasando todas las variables necesarias
    return render(request, 'usuarios/buy_product.html', {
        'producto': producto,
        'es_vendedor': es_vendedor,
        'tienda_inactiva': tienda_inactiva
    })
# =====================================================
# LISTA DE PRODUCTOS
# =====================================================
def lista_productos(request):
    # Obtener productos activos
    productos = Producto.objects.filter(activo=True)
    # Renderizar lista de productos
    return render(request, 'tiendas/list_products_store_seller.html', {
        'productos': productos
    })
# =====================================================
# BUSCADOR GENERAL
# =====================================================
def buscar(request):
    # Obtener consulta de búsqueda
    query = request.GET.get('q')
    productos = []
    tiendas = []
    
    if query:
        # Buscar productos por nombre, categoría o descripción, solo activos
        productos = Producto.objects.filter(
            Q(nombre__icontains=query) |
            Q(categoria__icontains=query) |
            Q(descripcion__icontains=query),
            activo=True
        )
        
        # Buscar tiendas por nombre o categoría, solo activas
        tiendas = Tienda.objects.filter(
            Q(nombre__icontains=query) |
            Q(categoria__icontains=query),
            activo=True
        )
    
    context = {
        "query": query,
        "productos": productos,
        "tiendas": tiendas
    }
    
    # Renderizar resultados de búsqueda
    return render(request, "productos/busqueda.html", context)

def sugerencias_busqueda(request):
    # Obtener texto de búsqueda
    query = request.GET.get("q", "").lower()

    # Obtener productos activos
    productos_db = Producto.objects.filter(activo=True)

    # Filtrar productos por nombre exacto (ignorar mayúsculas/minúsculas)
    productos = productos_db.filter(
        Q(nombre__icontains=query)
    )[:5]

    productos_sugeridos = []

    # Construir lista de productos sugeridos
    for producto in productos:
        imagen_url = ""
        # Obtener imagen principal del producto si existe
        imagen = producto.imagenes.first()  # Suponiendo que las imágenes están relacionadas con el producto
        if imagen:
            imagen_url = imagen.imagen.url
        productos_sugeridos.append({
            "nombre": producto.nombre,
            "precio": producto.precio,
            "categoria": producto.categoria,
            "imagen": imagen_url
        })

    # Obtener sugerencias de tiendas activas
    tiendas = list(
        Tienda.objects.filter(
            Q(nombre__icontains=query) |
            Q(categoria__icontains=query),
            activo=True  # Ahora utilizamos el campo 'activo' para filtrar las tiendas activas
        ).values("nombre")[:5]
    )

    # Retornar los resultados en formato JSON
    return JsonResponse({
        "productos": productos_sugeridos,
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