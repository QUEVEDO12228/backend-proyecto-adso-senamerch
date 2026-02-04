from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
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


def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Validar campos vacíos
        if not name or not phone or not email or not password:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('register')

        # Validar correo
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Ingresa un correo electrónico válido.')
            return redirect('register')

        # Verificar si el usuario ya existe
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
            return redirect('register')

        # Crear usuario
        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        messages.success(request, 'Cuenta creada correctamente. Inicia sesión.')
        return redirect('login')

    return render(request, 'usuarios/register.html')

def register_step_2(request):
    return render(request, 'usuarios/register2.html')

def forgot_password_view(request):
    context = {
        'form_submitted': False
    }

    if request.method == 'POST':
        context['form_submitted'] = True

        email = request.POST.get('email', '').strip()

        # Campo vacío
        if not email:
            messages.error(request, 'El correo es obligatorio.')
            return render(request, 'usuarios/forgot_password.html', context)

        # Validar correo
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Ingresa un correo válido.')
            return render(request, 'usuarios/forgot_password.html', context)

        # ✅ TODO OK → luego aquí enviarás el correo
        messages.success(request, 'Te enviamos un código a tu correo.')

        # 👉 REDIRECCIÓN LIMPIA (como login)
        return redirect('code_verify')

    return render(request, 'usuarios/forgot_password.html', context)


def code_verify_view(request):
    if request.method == 'POST':
        return redirect('reset_password')

    return render(request, 'usuarios/code_verify.html')



def reset_password_view(request):
    if request.method == 'POST':
        # luego aquí validas contraseñas y guardas
        return redirect('login')

    return render(request, 'usuarios/reset_password.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        query_type = request.POST.get('query_type', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not query_type or not message:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('contact')

        # Más adelante puedes guardar en BD o enviar correo
        messages.success(request, 'Tu mensaje fue enviado correctamente.')

        return redirect('contact')

    return render(request, 'usuarios/contact.html')