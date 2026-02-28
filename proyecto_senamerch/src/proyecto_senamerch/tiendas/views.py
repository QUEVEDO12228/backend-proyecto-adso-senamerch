import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Tienda
from productos.models import Producto
from django.contrib.auth import update_session_auth_hash
from usuarios.models import Profile, Address
from django.shortcuts import render, redirect


@login_required
def home_seller(request):

    # productos que NO sean de la tienda del vendedor
    productos = Producto.objects.exclude(
        tienda__propietario=request.user
    ).filter(activo=True)

    return render(request, "tiendas/card.html", {
        "productos": productos
    })

# ==========================================
# PASO 1 - DATOS BÁSICOS DE LA TIENDA
# ==========================================
@login_required
def create_store_view(request):

    # Evitar que cree más de una tienda
    if Tienda.objects.filter(propietario=request.user).exists():
        messages.warning(request, 'Ya tienes una tienda creada.')
        return redirect('home_client')

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        category = request.POST.get('category', '').strip()

        if not all([name, email, phone, category]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('tiendas:create_store')

        if len(name) < 3:
            messages.error(request, 'El nombre debe tener mínimo 3 caracteres.')
            return redirect('tiendas:create_store')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Correo inválido.')
            return redirect('tiendas:create_store')

        phone_clean = phone.replace(' ', '').replace('-', '')

        if not re.match(r'^(\+57)?[0-9]{10}$', phone_clean):
            messages.error(request, 'Teléfono inválido.')
            return redirect('tiendas:create_store')

        # Guardamos temporalmente en sesión
        request.session['store_data'] = {
            'name': name,
            'email': email,
            'phone': phone_clean,
            'category': category
        }

        return redirect('tiendas:create_store2')

    return render(request, 'tiendas/create_store.html')


# ==========================================
# PASO 2 - DESCRIPCIÓN E IMAGEN
# ==========================================
@login_required
def create_store2(request):

    store_data = request.session.get('store_data')

    if not store_data:
        messages.error(request, 'Debes completar el paso 1.')
        return redirect('tiendas:create_store')

    if request.method == 'POST':

        descripcion = request.POST.get('descripcion', '').strip()
        imagen = request.FILES.get('imagen')

        Tienda.objects.create(
            propietario=request.user,
            nombre=store_data['name'],
            email=store_data['email'],
            telefono=store_data['phone'],
            categoria=store_data['category'],
            descripcion=descripcion,
            imagen_portada=imagen
        )

        request.session.pop('store_data')

        messages.success(request, 'Tienda creada correctamente.')
        return redirect('home_client')

    return render(request, 'tiendas/create_store2.html')


# ==========================================
# DIRECCIÓN - PASO 1
# ==========================================
@login_required
def add_address_store(request):
    return render(request, 'tiendas/add_address_store.html')


# ==========================================
# DIRECCIÓN - PASO 2
# ==========================================
@login_required
def add_address_store2(request):

    if request.method == "POST":
        department = request.POST.get("department")
        city = request.POST.get("city")
        additional_info = request.POST.get("additional_info")

        messages.success(request, "Dirección guardada correctamente.")
        return redirect('home_client')

    return render(request, 'tiendas/add_address_store2.html')

@login_required
def profile_store_seller(request):
    # Traer la tienda
    tienda = Tienda.objects.filter(propietario=request.user).first()
    if not tienda:
        messages.warning(request, "Primero debes crear una tienda.")
        return redirect('tiendas:create_store')

    # Traer el perfil del usuario
    profile = getattr(request.user, 'profile', None)

    return render(request, 'tiendas/profile_store_seller.html', {
        'tienda': tienda,
        'profile': profile
    })
def store_orders(request):
    return render(request, 'tiendas/seller_catalog.html')

def seller_catalog(request):
    productos = Producto.objects.filter(tienda__propietario=request.user)
    return render(request, 'tiendas/seller_card.html', {
        'productos': productos
    })


@login_required
def edit_seller_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        # Guardamos los datos del paso 1 en sesión
        request.session['edit_user_data'] = {
            "email": request.POST.get("email", request.user.email),
            "first_name": request.POST.get("first_name", request.user.first_name),
            "telefono": request.POST.get("telefono", profile.phone)
        }

        # Guardar la imagen directamente si existe
        if "imagen" in request.FILES:
            profile.image = request.FILES["imagen"]
            profile.save()

        # Redirigir al paso 2
        return redirect('tiendas:edit_seller_profile2')

    return render(request, 'tiendas/edit_seller_profile.html', {
        "profile": profile,
    })


@login_required
def edit_seller_profile2(request):
    data_user = request.session.get('edit_user_data')
    data_address = request.session.get('edit_address_full')

    if not data_user:
        return redirect('tiendas:edit_seller_profile')

    if request.method == "POST":
        user = request.user
        profile = user.profile

        # =========================
        # GUARDAR DATOS DEL USUARIO
        # =========================
        user.email = data_user.get("email", user.email)
        user.first_name = data_user.get("first_name", user.first_name)
        user.save()

        profile.phone = data_user.get("telefono", profile.phone)

        # =========================
        # GUARDAR DIRECCIÓN SI EXISTE
        # =========================
        if data_address:
            profile.neighborhood = data_address.get("neighborhood")
            profile.address_number = data_address.get("address_number")
            profile.road_type = data_address.get("road_type")
            profile.postal_code = data_address.get("postal_code")
            profile.department = data_address.get("department")
            profile.city = data_address.get("city")
            profile.extra_info = data_address.get("additional_info")

        profile.save()

        # =========================
        # CONTRASEÑA
        # =========================
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password and confirm:
            if password != confirm:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect('tiendas:edit_seller_profile2')

            user.set_password(password)
            update_session_auth_hash(request, user)
            user.save()

        # =========================
        # LIMPIAR SESSION
        # =========================
        request.session.pop('edit_user_data', None)
        request.session.pop('edit_address_data', None)
        request.session.pop('edit_address_full', None)

        messages.success(request, "Perfil actualizado correctamente.")
        return redirect('tiendas:profile_store_seller')

    return render(request, 'tiendas/edit_seller_profile2.html', {
        "profile": request.user.profile
    })

@login_required
def edit_address_seller(request):
    """Paso 1: barrio, número, tipo de vía, código postal"""
    profile = request.user.profile

    if request.method == "POST":
        profile.neighborhood = request.POST.get("neighborhood", profile.neighborhood)
        profile.address_number = request.POST.get("address_number", profile.address_number)
        profile.road_type = request.POST.get("road_type", profile.road_type)
        profile.postal_code = request.POST.get("postal_code", profile.postal_code)
        profile.save()

        # Guardar los datos para paso 2 en sesión
        request.session['edit_address_data'] = {
            "neighborhood": profile.neighborhood,
            "address_number": profile.address_number,
            "road_type": profile.road_type,
            "postal_code": profile.postal_code
        }

        return redirect('tiendas:edit_address_seller2')

    return render(request, 'tiendas/add_adress_seller_edit.html', {
        "profile": profile
    })


@login_required
def edit_address_seller2(request):
    """Paso 2: departamento, ciudad, info adicional"""
    profile = request.user.profile
    data = request.session.get('edit_address_data', {})

    # Lista de departamentos para el template
    departamentos = ["Risaralda", "Quindío", "Caldas"]

    if request.method == "POST":
        department = request.POST.get("department", "").strip()
        city = request.POST.get("city", "").strip()
        additional_info = request.POST.get("additional_info", "").strip()

        # Validación simple
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

    tienda = Tienda.objects.filter(propietario=request.user).first()

    if not tienda:
        return redirect('tiendas:profile_store_seller')

    if request.method == "POST":

        request.session['edit_store_data'] = {
            "nombre": request.POST.get("nombre"),
            "email": request.POST.get("email"),
            "telefono": request.POST.get("telefono"),
            "categoria": request.POST.get("categoria"),
        }

        return redirect('tiendas:edit_store_seller2')

    return render(request, 'tiendas/edit_store_seller.html', {
        'tienda': tienda
    })


# ==========================================
# EDITAR TIENDA - PASO 2
# ==========================================
@login_required
def edit_store_seller2(request):

    tienda = Tienda.objects.filter(propietario=request.user).first()

    data = request.session.get('edit_store_data')

    if not tienda or not data:
        return redirect('tiendas:edit_store_seller')

    if request.method == "POST":

        tienda.nombre = data["nombre"]
        tienda.email = data["email"]
        tienda.telefono = data["telefono"]
        tienda.categoria = data["categoria"]
        tienda.descripcion = request.POST.get("descripcion")

        if request.FILES.get("imagen"):
            tienda.imagen_portada = request.FILES.get("imagen")

        tienda.save()

        request.session.pop('edit_store_data')

        messages.success(request, "Tienda actualizada correctamente.")

        return redirect('tiendas:profile_store_seller')

    return render(request, 'tiendas/edit_store_seller2.html', {
        'tienda': tienda
    })

def store_address_view(request):
    tienda = get_object_or_404(Tienda, propietario=request.user)

    return render(request, 'tiendas/store_admin_form.html', {
        'tienda': tienda,
        'direccion': tienda
    })


@login_required
def seller_address_view(request):
    # Traemos el perfil del usuario, no la tienda
    profile = request.user.profile

    return render(request, 'tiendas/seller_profile_address.html', {
        'profile': profile
    })

def profile_store_client(request, id):
    tienda = get_object_or_404(Tienda, id=id)

    return render(request, "tiendas/profile_store_client.html", {
        "tienda": tienda
    })

