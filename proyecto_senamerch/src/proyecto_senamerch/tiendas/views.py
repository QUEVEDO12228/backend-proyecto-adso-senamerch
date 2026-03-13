import re  # Para validaciones con expresiones regulares
from django.shortcuts import render, redirect, get_object_or_404  # Funciones para manejar vistas y redirecciones
from django.contrib import messages  # Sistema de mensajes de Django
from django.contrib.auth.decorators import login_required  # Decorador para requerir autenticación
from django.core.validators import validate_email  # Validador de correos electrónicos
from django.core.exceptions import ValidationError  # Excepción para validaciones
from productos.models import Producto  # Modelo de productos
from django.contrib.auth import update_session_auth_hash  # Mantener sesión activa tras cambio de contraseña
from usuarios.models import Profile, Address  # Modelos relacionados con usuario
from django.shortcuts import render, redirect  # Renderizar vistas y redirigir
from .models import Tienda  # Modelo de tienda
from pedidos.models import Pedido
from decimal import Decimal
# ==========================================
# INICIO DEL VENDEDOR
# ==========================================
@login_required
def home_seller(request):
    # Obtener productos activos que NO pertenezcan a la tienda del usuario
    productos = Producto.objects.exclude(
        tienda__propietario=request.user
    ).filter(activo=True)
    # Renderizar vista con los productos disponibles
    return render(request, "tiendas/card.html", {
        "productos": productos
    })
# ==========================================
# PASO 1 - DATOS BÁSICOS DE LA TIENDA
# ==========================================
@login_required
def create_store_view(request):
    # Evitar que el usuario cree más de una tienda
    if Tienda.objects.filter(propietario=request.user).exists():
        messages.warning(request, 'Ya tienes una tienda creada.')
        return redirect('tiendas:home_seller')
    if request.method == 'POST':
        # Obtener datos del formulario
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        category = request.POST.get('category', '').strip()
        # Validar campos obligatorios
        if not all([name, email, phone, category]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('tiendas:create_store')
        # Validar longitud mínima del nombre
        if len(name) < 3:
            messages.error(request, 'El nombre debe tener mínimo 3 caracteres.')
            return redirect('tiendas:create_store')
        # Validar formato del correo
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Correo inválido.')
            return redirect('tiendas:create_store')
        # Limpiar número de teléfono
        phone_clean = phone.replace(' ', '').replace('-', '')
        # Validar formato de teléfono colombiano
        if not re.match(r'^(\+57)?[0-9]{10}$', phone_clean):
            messages.error(request, 'Teléfono inválido.')
            return redirect('tiendas:create_store')
        # Guardar datos temporales en la sesión
        request.session['store_data'] = {
            'name': name,
            'email': email,
            'phone': phone_clean,
            'category': category
        }
        # Redirigir al paso 2
        return redirect('tiendas:create_store2')
    # Renderizar formulario del paso 1
    return render(request, 'tiendas/create_store.html')
# ==========================================
# PASO 2 - DESCRIPCIÓN E IMAGEN
# ==========================================
@login_required
def create_store2(request):
    # Obtener datos guardados en sesión
    store_data = request.session.get('store_data')
    store_address = request.session.get('store_address')
    # Validar que el paso 1 esté completado
    if not store_data:
        messages.error(request, 'Debes completar el paso 1.')
        return redirect('tiendas:create_store')
    if request.method == 'POST':
        # Validar que la dirección esté agregada
        if not store_address:
            messages.error(request, 'Debes agregar la dirección.')
            return redirect('tiendas:add_address_store')
        # Obtener descripción e imagen
        descripcion = request.POST.get('description', '').strip()
        imagen = request.FILES.get('cover')
        # Validar campos obligatorios
        if not descripcion or not imagen:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('tiendas:create_store2')
        # Crear la tienda con todos los datos recopilados
        Tienda.objects.create(
            propietario=request.user,
            nombre=store_data['name'],
            email=store_data['email'],
            telefono=store_data['phone'],
            categoria=store_data['category'],
            descripcion=descripcion,
            imagen_portada=imagen,
            barrio=store_address['neighborhood'],
            tipo_via=store_address['road_type'],
            codigo_postal=store_address['postal_code'],
            departamento=store_address['department'],
            municipio=store_address['city'],
            informacion_adicional=store_address['additional_info'],
        )
        # Limpiar datos de sesión
        request.session.pop('store_data', None)
        request.session.pop('store_address', None)
        messages.success(request, 'Tienda creada correctamente.')
        return redirect('tiendas:home_seller')
    # Renderizar formulario del paso 2
    return render(request, 'tiendas/create_store2.html')
# =====================================================
# DIRECCIÓN TIENDA - PASO 1
# =====================================================
@login_required
def add_address_store(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        neighborhood = request.POST.get('neighborhood', '').strip()
        address_number = request.POST.get('address_number', '').strip()
        road_type = request.POST.get('road_type', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        # Validar campos obligatorios
        if not neighborhood or not address_number:
            messages.error(request, 'Barrio y dirección obligatorios.')
            return redirect('tiendas:add_address_store')
        # Validar longitud mínima del barrio
        if len(neighborhood) < 3:
            messages.error(request, 'El barrio debe tener mínimo 3 caracteres.')
            return redirect('tiendas:add_address_store')
        # Validar longitud mínima de dirección
        if len(address_number) < 5:
            messages.error(request, 'Dirección inválida.')
            return redirect('tiendas:add_address_store')
        # Validar que el código postal sea numérico
        if postal_code and not postal_code.isdigit():
            messages.error(request, 'Código postal inválido.')
            return redirect('tiendas:add_address_store')
        # Guardar primera parte de la dirección
        request.session['store_address_step_1'] = {
            'neighborhood': neighborhood,
            'address_number': address_number,
            'road_type': road_type,
            'postal_code': postal_code,
        }
        request.session.modified = True  # Marcar sesión como modificada
        # Redirigir al paso 2 de dirección
        return redirect('tiendas:add_address_store2')
    # Renderizar formulario de dirección paso 1
    return render(request, 'tiendas/add_address_store.html')
@login_required
def add_address_store2(request):

    step_1 = request.session.get('store_address_step_1')

    if not step_1:
        messages.error(request, 'Debes completar el paso anterior.')
        return redirect('tiendas:add_address_store')

    if request.method == 'POST':

        department = request.POST.get('department', '').strip()
        city = request.POST.get('city', '').strip()
        additional_info = request.POST.get('additional_info', '').strip()

        if not department or not city:
            messages.error(request, 'Departamento y municipio obligatorios.')
            return redirect('tiendas:add_address_store2')

        request.session['store_address'] = {
            **step_1,
            'department': department,
            'city': city,
            'additional_info': additional_info,
        }

        request.session.modified = True
        request.session.pop('store_address_step_1', None)

        return redirect('tiendas:create_store2')

    return render(request, 'tiendas/add_address_store2.html')
@login_required
def profile_store_seller(request):
    # Obtener la tienda del usuario
    tienda = Tienda.objects.filter(propietario=request.user).first()
    # Verificar si el usuario tiene tienda creada
    if not tienda:
        messages.warning(request, "Primero debes crear una tienda.")
        return redirect('tiendas:create_store')
    # Obtener perfil del usuario si existe
    profile = getattr(request.user, 'profile', None)
    # Renderizar perfil de la tienda del vendedor
    return render(request, 'tiendas/profile_store_seller.html', {
        'tienda': tienda,
        'profile': profile
    })
@login_required
def seller_catalog(request):
    # Obtener la tienda del usuario
    tienda = Tienda.objects.filter(propietario=request.user).first()
    # Obtener productos que pertenecen al vendedor
    productos = Producto.objects.filter(
        tienda__propietario=request.user
    )
    # Renderizar catálogo del vendedor
    return render(request, 'tiendas/seller_card.html', {
        'productos': productos,
        'tienda': tienda   # Enviar tienda al template
    })
@login_required
def edit_seller_profile(request):
    # Obtener o crear perfil del usuario
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        # Guardar datos básicos del usuario en sesión
        request.session['edit_user_data'] = {
            "email": request.POST.get('email'),
            "first_name": request.POST.get('first_name'),
            "telefono": request.POST.get('telefono'),
        }
        # Guardar imagen de perfil si fue enviada
        if 'imagen' in request.FILES:
            profile.image = request.FILES['imagen']
            profile.save()
        request.session.modified = True  # Marcar sesión como modificada
        # Redirigir al paso 2 de edición
        return redirect('tiendas:edit_seller_profile2')
    # Renderizar formulario de edición
    return render(request, 'tiendas/edit_seller_profile.html', {
        'profile': profile
    })
@login_required
def edit_seller_profile2(request):
    # Obtener datos guardados en sesión
    data_user = request.session.get('edit_user_data')
    data_address = request.session.get('edit_address_full')
    # Validar que el paso anterior se haya completado
    if not data_user:
        return redirect('tiendas:edit_seller_profile')
    if request.method == "POST":
        user = request.user
        profile = user.profile
        # Actualizar datos básicos del usuario
        user.email = data_user.get("email", user.email)
        user.first_name = data_user.get("first_name", user.first_name)
        user.save()
        # Actualizar teléfono del perfil
        profile.phone = data_user.get("telefono", profile.phone)
        # Actualizar dirección si fue editada
        if data_address:
            profile.neighborhood = data_address.get("neighborhood")
            profile.address_number = data_address.get("address_number")
            profile.road_type = data_address.get("road_type")
            profile.postal_code = data_address.get("postal_code")
            profile.department = data_address.get("department")
            profile.city = data_address.get("city")
            profile.extra_info = data_address.get("additional_info")
        profile.save()
        # Obtener contraseñas del formulario
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")
        # Validar y actualizar contraseña
        if password and confirm:
            if password != confirm:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect('tiendas:edit_seller_profile2')
            user.set_password(password)
            update_session_auth_hash(request, user)  # Mantener sesión activa
            user.save()
        # Eliminar datos temporales de sesión
        request.session.pop('edit_user_data', None)
        request.session.pop('edit_address_data', None)
        request.session.pop('edit_address_full', None)
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect('tiendas:profile_store_seller')
    # Renderizar paso 2 de edición de perfil
    return render(request, 'tiendas/edit_seller_profile2.html', {
        "profile": request.user.profile
    })
@login_required
def edit_address_seller(request):
    """Paso 1: barrio, número, tipo de vía, código postal"""
    # Obtener perfil del usuario
    profile = request.user.profile
    if request.method == "POST":
        # Actualizar datos básicos de dirección
        profile.neighborhood = request.POST.get("neighborhood", profile.neighborhood)
        profile.address_number = request.POST.get("address_number", profile.address_number)
        profile.road_type = request.POST.get("road_type", profile.road_type)
        profile.postal_code = request.POST.get("postal_code", profile.postal_code)
        profile.save()
        # Guardar datos en sesión para el paso 2
        request.session['edit_address_data'] = {
            "neighborhood": profile.neighborhood,
            "address_number": profile.address_number,
            "road_type": profile.road_type,
            "postal_code": profile.postal_code
        }
        # Redirigir al paso 2
        return redirect('tiendas:edit_address_seller2')
    # Renderizar formulario de dirección paso 1
    return render(request, 'tiendas/add_adress_seller_edit.html', {
        "profile": profile
    })
@login_required
def edit_address_seller2(request):
    """Paso 2: departamento, ciudad, info adicional"""
    # Obtener perfil del usuario
    profile = request.user.profile
    # Recuperar datos guardados del paso 1
    data = request.session.get('edit_address_data', {})
    # Lista de departamentos para el formulario
    departamentos = ["Risaralda", "Quindío", "Caldas"]
    if request.method == "POST":
        department = request.POST.get("department", "").strip()
        city = request.POST.get("city", "").strip()
        additional_info = request.POST.get("additional_info", "").strip()
        # Validar campos obligatorios
        if not department or not city:
            messages.error(request, "Departamento y municipio son obligatorios.")
            return render(request, 'tiendas/add_adress_seller_edit2.html', {
                "profile": profile,
                "form_data": {
                    "department": department,
                    "city": city,
                    "additional_info": additional_info
                },
                "departamentos": departamentos
            })
        # Guardar todo en Profile
        profile.department = department
        profile.city = city
        profile.extra_info = additional_info
        # Guardar también los datos del paso 1 si existen en sesión
        profile.neighborhood = data.get("neighborhood", profile.neighborhood)
        profile.address_number = data.get("address_number", profile.address_number)
        profile.road_type = data.get("road_type", profile.road_type)
        profile.postal_code = data.get("postal_code", profile.postal_code)
        profile.save()
        # Limpiar sesión temporal
        request.session.pop('edit_address_data', None)
        messages.success(request, "Dirección actualizada correctamente.")
        return redirect('tiendas:edit_seller_profile2')
    return render(request, 'tiendas/add_adress_seller_edit2.html', {
        "profile": profile,
        "form_data": {},
        "departamentos": departamentos
    })
# ==========================================
# EDITAR TIENDA - PASO 1
# ==========================================
@login_required
def edit_store_seller(request):
    # Obtener tienda del vendedor
    tienda = Tienda.objects.filter(propietario=request.user).first()
    # Si no existe tienda, redirigir al perfil
    if not tienda:
        return redirect('tiendas:profile_store_seller')
    if request.method == "POST":
        # Guardar datos básicos de la tienda en sesión
        request.session['edit_store_data'] = {
            "nombre": request.POST.get("nombre"),
            "email": request.POST.get("email"),
            "telefono": request.POST.get("telefono"),
            "categoria": request.POST.get("categoria"),
        }
        # Redirigir al paso 2
        return redirect('tiendas:edit_store_seller2')
    # Renderizar formulario de edición
    return render(request, 'tiendas/edit_store_seller.html', {
        'tienda': tienda
    })
# ==========================================
# EDITAR TIENDA - PASO 2
# ==========================================
@login_required
def edit_store_seller2(request):
    # Obtener tienda y datos temporales
    tienda = Tienda.objects.filter(propietario=request.user).first()
    data = request.session.get('edit_store_data')
    # Validar existencia de tienda y datos
    if not tienda or not data:
        return redirect('tiendas:edit_store_seller')
    if request.method == "POST":
        # Actualizar datos básicos de la tienda
        tienda.nombre = data.get("nombre", tienda.nombre)
        tienda.email = data.get("email", tienda.email)
        tienda.telefono = data.get("telefono", tienda.telefono)
        tienda.categoria = data.get("categoria", tienda.categoria)
        # Actualizar descripción
        tienda.descripcion = request.POST.get("descripcion", tienda.descripcion)
        # Actualizar imagen si se envía una nueva
        if request.FILES.get("imagen"):
            tienda.imagen_portada = request.FILES.get("imagen")
        tienda.save()
        # Limpiar datos de sesión
        request.session.pop('edit_store_data', None)
        messages.success(request, "Tienda actualizada correctamente.")
        return redirect('tiendas:profile_store_seller')
    # Renderizar formulario del paso 2
    return render(request, 'tiendas/edit_store_seller2.html', {
        'tienda': tienda
    })
# ==========================================
# VISTA DIRECCIÓN DE LA TIENDA
# ==========================================
@login_required
def store_address_view(request):
    # Obtener tienda del vendedor
    tienda = Tienda.objects.filter(propietario=request.user).first()
    # Renderizar información de dirección
    return render(request, 'tiendas/store_profile_address.html', {
        'tienda': tienda,
        'direccion': tienda
    })
@login_required
def seller_address_view(request):
    # Obtener o crear perfil del usuario
    profile, created = Profile.objects.get_or_create(user=request.user)
    # Renderizar dirección del vendedor
    return render(request, "tiendas/seller_profile_address.html", {
        "profile": profile
    })
# ==========================================
# EDITAR DIRECCIÓN TIENDA - PASO 1
# ==========================================
@login_required
def edit_address_store(request):
    # Obtener tienda del vendedor
    tienda = Tienda.objects.filter(propietario=request.user).first()
    # Validar existencia de tienda
    if not tienda:
        messages.error(request, "Primero debes crear la tienda.")
        return redirect('tiendas:create_store')
    if request.method == "POST":
        # Obtener datos del formulario
        neighborhood = request.POST.get("neighborhood", "").strip()
        address_number = request.POST.get("address_number", "").strip()
        road_type = request.POST.get("road_type", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()
        # Validar campos obligatorios
        if not neighborhood or not address_number:
            messages.error(request, "Barrio y número de dirección son obligatorios.")
            return redirect('tiendas:edit_address_store')
        # Guardar datos temporalmente en sesión
        request.session['edit_store_address_step1'] = {
            "neighborhood": neighborhood,
            "address_number": address_number,
            "road_type": road_type,
            "postal_code": postal_code,
        }
        # Redirigir al paso 2
        return redirect('tiendas:edit_address_store2')
    # Renderizar formulario de dirección
    return render(request, "tiendas/add_address_store_edit.html", {
        "tienda": tienda
    })
# ==========================================
# EDITAR DIRECCIÓN TIENDA - PASO 2
# ==========================================
@login_required
def edit_address_store2(request):
    # Obtener tienda y datos del paso 1
    tienda = Tienda.objects.filter(propietario=request.user).first()
    step1 = request.session.get("edit_store_address_step1", {})
    # Validar existencia de tienda
    if not tienda:
        return redirect("tiendas:edit_address_store")
    # Lista de departamentos disponibles
    departamentos = ["Risaralda", "Quindío", "Caldas"]
    if request.method == "POST":
        # Obtener datos del formulario
        department = request.POST.get("department", "").strip()
        city = request.POST.get("city", "").strip()
        additional_info = request.POST.get("additional_info", "").strip()
        # Validar campos obligatorios
        if not department or not city:
            messages.error(request, "Departamento y municipio son obligatorios.")
            return render(request, "tiendas/add_address_store_edit2.html", {
                "tienda": tienda,
                "form_data": {
                    "department": department,
                    "city": city,
                    "additional_info": additional_info
                },
                "departamentos": departamentos
            })
        # Actualizar dirección de la tienda
        tienda.barrio = step1.get("neighborhood", tienda.barrio)
        tienda.numero_direccion = step1.get("address_number", tienda.numero_direccion)
        tienda.tipo_via = step1.get("road_type", tienda.tipo_via)
        tienda.codigo_postal = step1.get("postal_code", tienda.codigo_postal)
        tienda.departamento = department
        tienda.municipio = city
        tienda.informacion_adicional = additional_info
        tienda.save()
        # Limpiar datos de sesión
        request.session.pop("edit_store_address_step1", None)
        messages.success(request, "Dirección de la tienda actualizada correctamente.")
        return redirect("tiendas:edit_store_seller2")
    # Renderizar formulario paso 2
    return render(request, "tiendas/add_address_store_edit2.html", {
        "tienda": tienda,
        "form_data": {},
        "departamentos": departamentos
    })
@login_required
def list_products_store_seller(request):
    # Obtener tienda del vendedor
    tienda = Tienda.objects.filter(propietario=request.user).first()
    # Obtener productos del vendedor ordenados por fecha
    productos = Producto.objects.filter(
        tienda__propietario=request.user
    ).order_by('-creado_en')
    # Renderizar lista de productos
    return render(request, 'tiendas/list_products_store_seller.html', {
        'productos': productos,
        'tienda': tienda
    })
def profile_store_client(request, tienda_id):
    # Obtener tienda o devolver 404
    tienda = get_object_or_404(Tienda, id=tienda_id)
    # Obtener productos de la tienda con relaciones optimizadas
    productos = Producto.objects.filter(
        tienda=tienda
    ).select_related('tienda').prefetch_related('imagenes')
    # Renderizar productos para cliente
    return render(request, 'usuarios/store_products_client.html', {
        'productos': productos,
        'tienda': tienda
    })
def sales_details_order_store(request, pedido_id):
    # Obtener pedido o devolver 404
    pedido = get_object_or_404(Pedido, id=pedido_id)
    # Serializar datos del pedido para uso en JSON
    pedido_data = {
        "id": pedido.id,
        "fecha": pedido.creado_en.strftime("%d/%m/%Y"),
        "cliente": pedido.usuario.get_full_name(),
        "email": pedido.usuario.email,
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
    # Contexto para el template
    context = {
        "pedido": pedido,
        "pedido_json": pedido_data,  # Datos preparados para json_script
    }
    # Renderizar detalle de venta
    return render(request, "tiendas/sales_details_order_store.html", context)