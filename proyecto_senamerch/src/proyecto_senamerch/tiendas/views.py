import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import Tienda
from productos.models import Producto

def home_seller(request):
    products = Producto.objects.filter(tienda__propietario=request.user)

    return render(request, 'tiendas/home_seller.html', {
        'products': products
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

    tienda = Tienda.objects.filter(propietario=request.user).first()

    if not tienda:
        messages.warning(request, "Primero debes crear una tienda.")
        return redirect('tiendas:create_store')

    return render(request, 'tiendas/profile_store_seller.html', {
        'tienda': tienda
    })

def store_orders(request):
    return render(request, 'tiendas/seller_catalog.html')

def seller_catalog(request):
    return render(request, 'tiendas/seller_catalog.html')




def view_description_product_seller(request, id):
    context = {
        "product_id": id
    }
    return render(request, 'tiendas/view_description_product_seller.html', context)

@login_required
def edit_seller_profile(request):

    if request.method == "POST":

        # Guardamos datos temporales en sesión
        request.session['edit_user_data'] = {
            "email": request.POST.get("email"),
            "first_name": request.POST.get("first_name"),
        }

        return redirect('tiendas:edit_seller_profile2')

    return render(request, 'tiendas/edit_seller_profile.html')

# ==========================================
# EDITAR TIENDA - PASO 2
# ==========================================
from django.contrib.auth import update_session_auth_hash

@login_required
def edit_seller_profile2(request):

    data = request.session.get('edit_user_data')

    if not data:
        return redirect('tiendas:edit_seller_profile')

    if request.method == "POST":

        user = request.user

        # Guardar datos básicos
        user.email = data["email"]
        user.first_name = data["first_name"]

        # Guardar contraseña si existe
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password and confirm:
            if password != confirm:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect('tiendas:edit_seller_profile2')

            user.set_password(password)
            update_session_auth_hash(request, user)

        user.save()

        request.session.pop('edit_user_data')

        messages.success(request, "Perfil actualizado correctamente.")

        return redirect('tiendas:profile_store_seller')

    return render(request, 'tiendas/edit_seller_profile2.html')

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