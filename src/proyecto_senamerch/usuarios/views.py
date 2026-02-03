from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def login_view(request):
    context = {
        'form_submitted': False
    }

    if request.method == 'POST':
        context['form_submitted'] = True

        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Campos vacíos
        if not email or not password:
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'usuarios/login.html', context)

        # Validar correo
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Ingresa un correo electrónico válido.')
            return render(request, 'usuarios/login.html', context)

        # Autenticación
        user = authenticate(request, username=email, password=password)

        if user is None:
            messages.error(
                request,
                'Correo o contraseña incorrectos. ¿Aún no tienes cuenta? Regístrate.'
            )
            return render(request, 'usuarios/login.html', context)

        login(request, user)
        return redirect('home')

    return render(request, 'usuarios/login.html', context)
