import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import Tienda



@login_required
def create_store_view(request):
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
            return redirect('create_store')

        if len(name) < 3:
            messages.error(request, 'El nombre debe tener mínimo 3 caracteres.')
            return redirect('create_store')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Correo inválido.')
            return redirect('create_store')

        phone_clean = phone.replace(' ', '').replace('-', '')

        if not re.match(r'^(\+57)?[0-9]{10}$', phone_clean):
            messages.error(request, 'Teléfono inválido.')
            return redirect('create_store')

        request.session['store_data'] = {
            'name': name,
            'email': email,
            'phone': phone_clean,
            'category': category
        }

        return redirect('create_store_step_2')

    return render(request, 'usuarios/create_store.html')

@login_required
def create_store_step_2_view(request):

    store_data = request.session.get('store_data')

    if not store_data:
        messages.error(request, 'Debes completar el paso 1.')
        return redirect('create_store')

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

    return render(request, 'usuarios/create_store_step_2.html')