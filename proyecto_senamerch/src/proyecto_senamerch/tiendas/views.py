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

    tienda = Tienda.objects.get(propietario=request.user)

    return render(request, 'tiendas/profile_store_seller.html', {
        'tienda': tienda
    })
from django.shortcuts import render

def store_orders(request):

    orders = [
        {
            "id": 235,
            "date": "25/10/2025",
            "status": "Pendiente",
            "status_class": "pending",
            "total": 150000,
            "client": {
                "name": "Juan Pérez",
                "email": "JuanPerez12@gmail.com",
                "phone": "3102873825",
            },
            "address": {
                "neighborhood": "Buenos Aires",
                "street": "10 #34-36",
                "road_type": "Carrera",
                "postal_code": "101010101",
                "department": "Antioquia",
                "city": "Medellín",
            },
            "products": [
                {"name": "Tomate chonto", "quantity": "4 kg", "price": 24000},
                {"name": "Papa pastusa", "quantity": "3 kg", "price": 18000},
            ]
        },
        {
            "id": 236,
            "date": "28/10/2025",
            "status": "En proceso",
            "status_class": "pending",
            "total": 98500,
            "client": {
                "name": "Carlos Ruiz",
                "email": "carlosR@gmail.com",
                "phone": "3159902211",
            },
            "address": {
                "neighborhood": "La Floresta",
                "street": "Calle 54 # 67",
                "road_type": "Calle",
                "postal_code": "050030",
                "department": "Antioquia",
                "city": "Medellín",
            },
            "products": [
                {"name": "Aguacate hass", "quantity": "2 kg", "price": 16000},
                {"name": "Banano", "quantity": "6 unidades", "price": 5500},
            ]
        }
    ]

    return render(request, 'tiendas/store_orders.html', {"orders": orders})

def seller_catalog(request):
    return render(request, 'tiendas/seller_catalog.html')




def view_description_product_seller(request, id):
    context = {
        "product_id": id
    }
    return render(request, 'tiendas/view_description_product_seller.html', context)