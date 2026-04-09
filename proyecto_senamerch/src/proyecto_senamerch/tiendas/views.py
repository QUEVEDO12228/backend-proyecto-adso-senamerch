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
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from productos.models import Producto, Calificacion
@login_required
def home_seller(request):

    productos = Producto.objects.exclude(
        tienda__propietario=request.user
    ).filter(
        activo=True,
        tienda__activo=True  # CLAVE
    ).select_related(
        'tienda'
    ).prefetch_related(
        'imagenes'
    )

    calificaciones = Calificacion.objects.filter(
        usuario=request.user
    )

    cal_dict = {
        c.producto_id: c.puntuacion
        for c in calificaciones
    }

    for producto in productos:
        producto.user_rating = cal_dict.get(producto.id, 0)

    return render(request, "tiendas/card.html", {
        "productos": productos
    })
# ---> Lógica Creación tienda. PASO 1 - DATOS BÁSICOS DE LA TIENDA
@login_required
def create_store_view(request):
    # ---> Evitar que el usuario cree más de una tienda
    if Tienda.objects.filter(propietario=request.user).exists():
        messages.warning(request, 'Ya tienes una tienda creada.')
        return redirect('tiendas:home_seller')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        category = request.POST.get('category', '').strip()
        # ---> VALIDACIONES BÁSICAS
        if not all([name, email, phone, category]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('tiendas:create_store')
        if len(name) < 3:
            messages.error(request, 'El nombre debe tener mínimo 3 caracteres.')
            return redirect('tiendas:create_store')
        # ---> VALIDAR NOMBRE ÚNICO
        if Tienda.objects.filter(nombre__iexact=name).exists():
            messages.error(request, 'Ese nombre de tienda ya está en uso.')
            return redirect('tiendas:create_store')
        # ---> VALIDAR EMAIL ÚNICO
        if Tienda.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Ese correo ya está en uso.')
            return redirect('tiendas:create_store')
        # ---> VALIDAR EMAIL FORMATO
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Correo inválido.')
            return redirect('tiendas:create_store')
        # ---> VALIDAR TELÉFONO
        phone_clean = phone.replace(' ', '').replace('-', '')
        if not re.match(r'^(\+57)?[0-9]{10}$', phone_clean):
            messages.error(request, 'Teléfono inválido.')
            return redirect('tiendas:create_store')
        # ---> GUARDAR EN SESIÓN
        request.session['store_data'] = {
            'name': name,
            'email': email,
            'phone': phone_clean,
            'category': category
        }
        request.session.modified = True
        return redirect('tiendas:create_store2')
    return render(request, 'tiendas/create_store.html')
# ---> Lógica Creación tienda. PASO 2 - DATOS BÁSICOS DE LA TIENDA
@login_required
def create_store2(request):
    store_data = request.session.get('store_data')
    store_address = request.session.get('store_address', {})
    store_temp = request.session.get('store_temp', {})
    if not store_data:
        messages.error(request, 'Debes completar el paso 1.')
        return redirect('tiendas:create_store')
    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        imagen = request.FILES.get('cover')
        store_temp = store_temp.copy()
        store_temp['description'] = description
        # ---> GUARDAR IMAGEN EN /media/temp/
        if imagen:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp'))
            filename = fs.save(imagen.name, imagen)
            store_temp['imagen_name'] = filename
        request.session['store_temp'] = store_temp
        request.session.modified = True
        # ---> VALIDACIONES
        if not store_address:
            messages.error(request, 'Debes agregar la dirección.')
            return redirect('tiendas:add_address_store')
        if not description:
            messages.error(request, 'La descripción es obligatoria.')
            return render(request, 'tiendas/create_store2.html', {'store_temp': store_temp})
        if not imagen and not store_temp.get('imagen_name'):
            messages.error(request, 'Debes subir una imagen.')
            return render(request, 'tiendas/create_store2.html', {'store_temp': store_temp})
        # ---> VALIDAR NOMBRE ÚNICO (por seguridad)
        if Tienda.objects.filter(nombre__iexact=store_data['name']).exists():
            messages.error(request, 'Ya existe una tienda con ese nombre.')
            return redirect('tiendas:create_store')
        # ---> RECUPERAR IMAGEN CORRECTAMENTE
        imagen_final = None
        if imagen:
            imagen_final = imagen
        elif store_temp.get('imagen_name'):
            temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', store_temp['imagen_name'])
            with open(temp_path, 'rb') as f:
                imagen_final = File(f, name=store_temp['imagen_name'])
                # ---> Se crea File en memoria y el archivo se cierra al salir del with
        # ---> CREAR TIENDA
        tienda = Tienda.objects.create(
            propietario=request.user,
            nombre=store_data['name'],
            email=store_data['email'],
            telefono=store_data['phone'],
            categoria=store_data['category'],
            descripcion=description,
            imagen_portada=imagen_final,
            barrio=store_address.get('neighborhood', ''),
            numero_direccion=store_address.get('address_number', ''),
            tipo_via=store_address.get('road_type', ''),
            codigo_postal=store_address.get('postal_code', ''),
            departamento=store_address.get('department', ''),
            municipio=store_address.get('city', ''),
            informacion_adicional=store_address.get('additional_info', ''),
        )
        # ---> BORRAR IMAGEN TEMPORAL
        if store_temp.get('imagen_name'):
            temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', store_temp['imagen_name'])
            try:
                os.remove(temp_path)
            except PermissionError:
                # ---> Windows bloqueó el archivo, intentar eliminar más tarde
                pass
        # ---> LIMPIAR SESIÓN
        request.session.pop('store_data', None)
        request.session.pop('store_address', None)
        request.session.pop('store_temp', None)
        messages.success(request, 'Tienda creada correctamente.')
        return redirect('tiendas:home_seller')
    return render(request, 'tiendas/create_store2.html', {
        'store_temp': store_temp
    })
# ---> Lógica para agreagr la dirección de la tienda.
@login_required
def add_address_store(request):
    # ---> Primero buscar step_1, si no existe usar step_2 (store_address)
    data = request.session.get('store_address_step_1', {})
    if not data:
        data = request.session.get('store_address', {})
    if request.method == 'POST':
        neighborhood = request.POST.get('neighborhood', '').strip()
        address_number = request.POST.get('address_number', '').strip()
        road_type = request.POST.get('road_type', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        # ---> Guardar en sesión step_1 siempre
        request.session['store_address_step_1'] = {
            'neighborhood': neighborhood,
            'address_number': address_number,
            'road_type': road_type,
            'postal_code': postal_code,
        }
        request.session.modified = True
        # ---> Validaciones
        if not neighborhood or not address_number:
            messages.error(request, 'Barrio y dirección obligatorios.')
            return redirect('tiendas:add_address_store')
        if len(neighborhood) < 3:
            messages.error(request, 'El barrio debe tener mínimo 3 caracteres.')
            return redirect('tiendas:add_address_store')
        if len(address_number) < 5:
            messages.error(request, 'Dirección inválida.')
            return redirect('tiendas:add_address_store')
        if postal_code and not postal_code.isdigit():
            messages.error(request, 'Código postal inválido.')
            return redirect('tiendas:add_address_store')
        return redirect('tiendas:add_address_store2')
    return render(request, 'tiendas/add_address_store.html', {
        'data': data
    })
# ---> Lógica para terminar de agregar la dirección de la tienda.
@login_required
def add_address_store2(request):
    step_1 = request.session.get('store_address_step_1', {})
    step_2 = request.session.get('store_address', {})
    # ---> Combinar datos de step_1 y step_2 para mostrar en el template
    data = {**step_1, **step_2}  # step_2 sobrescribe step_1 si hay datos
    if not step_1 and not step_2:
        messages.error(request, 'Debes completar el paso anterior.')
        return redirect('tiendas:add_address_store')
    if request.method == 'POST':
        department = request.POST.get('department', '').strip()
        city = request.POST.get('city', '').strip()
        additional_info = request.POST.get('additional_info', '').strip()
        # ---> Guardar todos los datos en la sesión
        request.session['store_address'] = {
            **step_1,
            'department': department,
            'city': city,
            'additional_info': additional_info,
        }
        request.session.modified = True
        # ---> Limpiar step_1 porque ya se combinó
        request.session.pop('store_address_step_1', None)
        messages.success(request, 'Dirección agregada correctamente')
        return redirect('tiendas:create_store2')
    return render(request, 'tiendas/add_address_store2.html', {
        'data': data
    })
# ---> Lógica para visualizar el perfil del vendedor.
@login_required
def profile_store_seller(request):
    # ---> Obtener la tienda del usuario
    tienda = Tienda.objects.filter(propietario=request.user).first()
    # ---> Verificar si el usuario tiene tienda creada
    if not tienda:
        messages.warning(request, "Primero debes crear una tienda.")
        return redirect('tiendas:create_store')
    # ---> Obtener perfil del usuario si existe
    profile = getattr(request.user, 'profile', None)
    # ---> Renderizar perfil de la tienda del vendedor
    return render(request, 'tiendas/profile_store_seller.html', {
        'tienda': tienda,
        'profile': profile
    })
# ---> Lógica para deshabilitar la tienda.
@login_required
def disable_store(request):
    if request.method == "POST":
        tienda = Tienda.objects.get(propietario=request.user)
        tienda.activo = False
        tienda.save()
        print("TIENDA DESHABILITADA:", tienda.activo)
    return redirect('usuarios:home_client')
# ---> Lógica para habilitar tienda.
@login_required
def enable_store(request):
    tienda = get_object_or_404(Tienda, propietario=request.user)
    tienda.activo = True
    tienda.save()
    messages.success(request, "Tienda habilitada nuevamente.")
    return redirect('tiendas:profile_store_seller')
# ---> Lógica para visualizar el catalogo de la tienda.
@login_required
def seller_catalog(request):
    # ---> Obtener la tienda del usuario
    tienda = Tienda.objects.filter(propietario=request.user).first()
    # ---> Obtener productos que pertenecen al vendedor
    productos = Producto.objects.filter(
        tienda__propietario=request.user
    )
    # ---> Renderizar catálogo del vendedor
    return render(request, 'tiendas/seller_card.html', {
        'productos': productos,
        'tienda': tienda   # Enviar tienda al template
    })
# ---> Editar el perfil del vendedor paso 1.
@login_required
def edit_seller_profile(request):
    # ---> Obtener o crear perfil del usuario
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        # ---> Guardar datos básicos del usuario en sesión
        request.session['edit_user_data'] = {
            "email": request.POST.get('email'),
            "first_name": request.POST.get('first_name'),
            "telefono": request.POST.get('telefono'),
        }
        # ---> Guardar imagen de perfil si fue enviada
        if 'imagen' in request.FILES:
            profile.image = request.FILES['imagen']
            profile.save()
        request.session.modified = True  # ---> Marcar sesión como modificada
        # ---> Redirigir al paso 2 de edición
        return redirect('tiendas:edit_seller_profile2')
    # ---> Renderizar formulario de edición
    return render(request, 'tiendas/edit_seller_profile.html', {
        'profile': profile
    })
# ---> Editar el perfil del vendedor paso 2.
# ---> Edición del perfil del vendedor (paso 2) con guardado y redirección al perfil de tienda
@login_required
def edit_seller_profile2(request):

    data_user = request.session.get('edit_user_data')
    data_address = request.session.get('edit_address_full')

    # 🔴 Validación clave
    if not data_user:
        messages.warning(request, "Primero debes completar el paso 1.")
        return redirect('tiendas:edit_seller_profile')

    if request.method == "POST":

        user = request.user
        profile = user.profile

        # -------------------------
        # 🔹 ACTUALIZAR USUARIO
        # -------------------------
        user.email = data_user.get("email", user.email)
        user.first_name = data_user.get("first_name", user.first_name)
        user.save()

        # -------------------------
        # 🔹 ACTUALIZAR PERFIL
        # -------------------------
        profile.phone = data_user.get("telefono", profile.phone)

        if data_address:
            profile.neighborhood = data_address.get("neighborhood", profile.neighborhood)
            profile.address_number = data_address.get("address_number", profile.address_number)
            profile.road_type = data_address.get("road_type", profile.road_type)
            profile.postal_code = data_address.get("postal_code", profile.postal_code)
            profile.department = data_address.get("department", profile.department)
            profile.city = data_address.get("city", profile.city)
            profile.extra_info = data_address.get("additional_info", profile.extra_info)

        profile.save()

        # -------------------------
        # 🔹 CAMBIO DE CONTRASEÑA
        # -------------------------
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password or confirm:

            if password != confirm:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect('tiendas:edit_seller_profile2')

            if len(password) < 8:
                messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
                return redirect('tiendas:edit_seller_profile2')

            user.set_password(password)
            user.save()

            # 🔥 Mantener sesión activa
            update_session_auth_hash(request, user)

            messages.success(request, "Contraseña actualizada correctamente.")

        # -------------------------
        # 🔹 LIMPIAR SESIÓN
        # -------------------------
        request.session.pop('edit_user_data', None)
        request.session.pop('edit_address_full', None)

        # -------------------------
        # 🔹 MENSAJE FINAL
        # -------------------------
        messages.success(request, "Perfil actualizado correctamente.")

        return redirect('tiendas:profile_store_seller')

    # -------------------------
    # 🔹 GET
    # -------------------------
    return render(request, 'tiendas/edit_seller_profile2.html', {
        "profile": request.user.profile
    })
# ---> Editar dirección del perfil del vendedor paso 1.
@login_required
def edit_address_seller(request):
    """Paso 1: barrio, número, tipo de vía, código postal"""
    # ---> Obtener perfil del usuario
    profile = request.user.profile
    if request.method == "POST":
        # ---> Actualizar datos de dirección usando los campos existentes en el modelo
        profile.neighborhood = request.POST.get("neighborhood", profile.neighborhood)
        profile.address_number = request.POST.get("address_number", profile.address_number)
        profile.road_type = request.POST.get("road_type", profile.road_type)
        profile.postal_code = request.POST.get("postal_code", profile.postal_code)
        profile.save()
        # ---> Guardar datos en sesión para el paso 2
        request.session['edit_address_data'] = {
            "neighborhood": profile.neighborhood,
            "address_number": profile.address_number,
            "road_type": profile.road_type,
            "postal_code": profile.postal_code
        }
        # ---> Redirigir al paso 2
        return redirect('tiendas:edit_address_seller2')
    # ---> Renderizar formulario de dirección paso 1
    return render(request, 'tiendas/add_adress_seller_edit.html', {
        "profile": profile
    })
# ---> Editar dirección del perfil del vendedor paso 2.
@login_required
def edit_address_seller2(request):
    """Paso 2: departamento, ciudad, info adicional"""
    profile = request.user.profile
    # ---> Recuperar datos guardados del paso 1
    data = request.session.get('edit_address_data', {})
    departamentos = ["Risaralda", "Quindío", "Caldas"]
    if request.method == "POST":
        department = request.POST.get("department", "").strip()
        city = request.POST.get("city", "").strip()
        additional_info = request.POST.get("additional_info", "").strip()
        if not department or not city:
            messages.error(request, "Departamento y municipio son obligatorios.")
            return render(request, 'tiendas/add_address_seller_edit2.html', {  # CORREGIDO
                "profile": profile,
                "form_data": {
                    "department": department,
                    "city": city,
                    "additional_info": additional_info
                },
                "departamentos": departamentos
            })
        # ---> Guardar los datos del paso 2
        profile.department = department
        profile.city = city
        profile.extra_info = additional_info
        # ---> Guardar también los datos del paso 1 desde sesión
        profile.neighborhood = data.get("neighborhood", profile.neighborhood)
        profile.address_number = data.get("address_number", profile.address_number)
        profile.road_type = data.get("road_type", profile.road_type)
        profile.postal_code = data.get("postal_code", profile.postal_code)
        profile.save()
        # ---> Limpiar sesión
        request.session.pop('edit_address_data', None)
        messages.success(request, "Dirección actualizada correctamente.")
        return redirect('tiendas:edit_seller_profile2')
    # ---> GET
    return render(request, 'tiendas/add_adress_seller_edit2.html', {  # CORREGIDO
        "profile": profile,
        "form_data": {
            "department": profile.department,
            "city": profile.city,
            "additional_info": profile.extra_info
        },
        "departamentos": departamentos
    })
# ---> Editar el perfil de la tienda paso 1.
@login_required
def edit_store_seller(request):
    # ---> Obtener tienda del vendedor
    tienda = Tienda.objects.filter(propietario=request.user).first()
    # ---> Si no existe tienda, redirigir al perfil
    if not tienda:
        return redirect('tiendas:profile_store_seller')
    if request.method == "POST":
        # ---> Guardar datos básicos de la tienda en sesión
        request.session['edit_store_data'] = {
            "nombre": request.POST.get("nombre"),
            "email": request.POST.get("email"),
            "telefono": request.POST.get("telefono"),
            "categoria": request.POST.get("categoria"),
        }
        # ---> Redirigir al paso 2
        return redirect('tiendas:edit_store_seller2')
    # ---> Renderizar formulario de edición
    return render(request, 'tiendas/edit_store_seller.html', {
        'tienda': tienda
    })
# ---> Editar el perfil de la tienda paso 2
@login_required
def edit_store_seller2(request):
    tienda = Tienda.objects.filter(propietario=request.user).first()
    data = request.session.get('edit_store_data')
    if not tienda or not data:
        return redirect('tiendas:edit_store_seller')
    if request.method == "POST":
        # ---> DATOS BÁSICOS
        tienda.nombre = data.get("nombre", tienda.nombre)
        tienda.email = data.get("email", tienda.email)
        tienda.telefono = data.get("telefono", tienda.telefono)
        tienda.categoria = data.get("categoria", tienda.categoria)
        # ---> DESCRIPCIÓN
        descripcion = request.POST.get("descripcion", "").strip()
        if not descripcion:
            messages.error(request, "La descripción es obligatoria.")
            return render(request, 'tiendas/edit_store_seller2.html', {
                'tienda': tienda
            })
        tienda.descripcion = descripcion
        # ---> IMAGEN 
        imagen = request.FILES.get("imagen")
        if imagen:
            # eliminar anterior (PRO)
            if tienda.imagen_portada:
                tienda.imagen_portada.delete(save=False)
            tienda.imagen_portada = imagen
        # ---> GUARDAR
        tienda.save()
        # ---> LIMPIAR SESIÓN
        request.session.pop('edit_store_data', None)
        # ---> MENSAJE
        messages.success(request, "Cambios guardados correctamente.")
        # ---> REDIRECT (MEJOR PRÁCTICA)
        return redirect('tiendas:profile_store_seller')
    return render(request, 'tiendas/edit_store_seller2.html', {
        'tienda': tienda
    })
# ---> Visualizar el perfil de la direccción de la tienda 
@login_required
def store_address_view(request):
    # ---> Obtener tienda del vendedor
    tienda = Tienda.objects.filter(propietario=request.user).first()
    # ---> Renderizar información de dirección
    return render(request, 'tiendas/store_profile_address.html', {
        'tienda': tienda,
        'direccion': tienda
    })
@login_required
# ---> Visualizar la dirección del vendedor.
def seller_address_view(request):
    # Perfil del usuario
    profile, created = Profile.objects.get_or_create(user=request.user)

    # 🔥 Obtener dirección real del usuario (modelo Address)
    address = request.user.addresses.first()

    return render(request, "tiendas/seller_profile_address.html", {
        "profile": profile,
        "address": address
    })
# ---> Editar la dirección del perfil de la tienda paso 1 DATOS BÁSICOS
@login_required
def edit_address_store(request):
    # --> Obtener tienda del vendedor
    tienda = Tienda.objects.filter(propietario=request.user).first()
    # ---> Validar existencia de tienda
    if not tienda:
        messages.error(request, "Primero debes crear la tienda.")
        return redirect('tiendas:create_store')
    if request.method == "POST":
        # ---> Obtener datos del formulario
        neighborhood = request.POST.get("neighborhood", "").strip()
        address_number = request.POST.get("address_number", "").strip()
        road_type = request.POST.get("road_type", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()
        # ---> Validar campos obligatorios
        if not neighborhood or not address_number:
            messages.error(request, "Barrio y número de dirección son obligatorios.")
            return redirect('tiendas:edit_address_store')
        # ---> GUARDAR EN BASE DE DATOS
        tienda.barrio = neighborhood
        tienda.numero_direccion = address_number
        tienda.tipo_via = road_type
        tienda.codigo_postal = postal_code
        tienda.save()
        messages.success(request, "Dirección actualizada correctamente.")
        # ---> Redirigir al paso 2
        return redirect('tiendas:edit_address_store2')
    # ---> GET → mostrar formulario con datos actuales
    return render(request, "tiendas/add_address_store_edit.html", {
        "tienda": tienda
    })
# ---> Editar la dirección del perfil de la tienda paso 2 DATOS BÁSICOS
@login_required
def edit_address_store2(request):
    tienda = Tienda.objects.filter(propietario=request.user).first()
    if not tienda:
        return redirect("tiendas:edit_address_store")
    departamentos = ["Risaralda", "Quindío", "Caldas"]
    if request.method == "POST":
        department = request.POST.get("department", "").strip()
        city = request.POST.get("city", "").strip()
        additional_info = request.POST.get("additional_info", "").strip()
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
        # ---> GUARDAR DIRECTO (SIN SESSION)
        tienda.departamento = department
        tienda.municipio = city
        tienda.informacion_adicional = additional_info
        tienda.save()
        messages.success(request, "Dirección de la tienda actualizada correctamente.")
        return redirect("tiendas:edit_store_seller2")
    return render(request, "tiendas/add_address_store_edit2.html", {
        "tienda": tienda,
        "form_data": {},
        "departamentos": departamentos
    })
# ---> Lógica para el listado de prodcutos de la tienda
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
# ---> Lógica para visualizar la tienda y sus productos como cliente.
def profile_store_client(request, tienda_id):
    # ---> Obtener tienda o devolver 404
    tienda = get_object_or_404(Tienda, id=tienda_id)
    # ---> Obtener productos de la tienda
    productos = Producto.objects.filter(
        tienda=tienda
    ).select_related(
        'tienda'
    ).prefetch_related(
        'imagenes'
    )
    # ---> Validar si el usuario está autenticado
    if request.user.is_authenticated:
        calificaciones = Calificacion.objects.filter(
            usuario=request.user
        )
        cal_dict = {
            c.producto_id: c.puntuacion
            for c in calificaciones
        }
        for producto in productos:
            producto.user_rating = cal_dict.get(producto.id, 0)
    else:
        for producto in productos:
            producto.user_rating = 0
    return render(request, 'usuarios/store_products_client.html', {
        'productos': productos,
        'tienda': tienda
    })
" ---> Lógica para el detalle del pedido de la tienda."
def sales_details_order_store(request, pedido_id):
    # ---> Obtener pedido o devolver 404
    pedido = get_object_or_404(Pedido, id=pedido_id)
    # ---> Serializar datos del pedido para uso en JSON
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
    # ---> Contexto para el template
    context = {
        "pedido": pedido,
        "pedido_json": pedido_data,  # Datos preparados para json_script
    }
    # Renderizar detalle de venta
    return render(request, "tiendas/sales_details_order_store.html", context)
