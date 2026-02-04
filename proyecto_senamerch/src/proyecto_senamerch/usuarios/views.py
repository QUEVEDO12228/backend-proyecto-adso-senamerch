import re
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password


# =========================
# LOGIN (NO TOCADO)
# =========================

def login_view(request):
    context = {'form_submitted': False}

    if request.method == 'POST':
        context['form_submitted'] = True

        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not email or not password:
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'usuarios/login.html', context)

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Ingresa un correo electrónico válido.')
            return render(request, 'usuarios/login.html', context)

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


# =========================
# REGISTRO PROFESIONAL (NO HELPED)
# =========================

def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not all([name, phone, email, password, password_confirm]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('register')

        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]{3,}$', name):
            messages.error(request, 'El nombre debe tener al menos 3 letras y no números.')
            return redirect('register')

        phone_clean = phone.replace(' ', '').replace('-', '')

        if not re.match(r'^(\+57)?[0-9]{10}$', phone_clean):
            messages.error(request, 'Número de teléfono inválido.')
            return redirect('register')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Correo electrónico inválido.')
            return redirect('register')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
            return redirect('register')

        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('register')

        if (
            len(password) < 8 or
            not re.search(r'[A-Z]', password) or
            not re.search(r'[0-9]', password)
        ):
            messages.error(
                request,
                'La contraseña debe tener mínimo 8 caracteres, una mayúscula y un número.'
            )
            return redirect('register')

        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        messages.success(request, 'Cuenta creada correctamente. Inicia sesión.')
        return redirect('login')

    return render(request, 'usuarios/register.html')


# =========================
# REGISTRO PASO 2
# =========================

def register_step_2(request):
    return render(request, 'usuarios/register2.html')


# =========================
# RECUPERAR CONTRASEÑA (CON ENVÍO REAL)
# =========================

def forgot_password_view(request):
    context = {'form_submitted': False}

    if request.method == 'POST':
        context['form_submitted'] = True
        email = request.POST.get('email', '').strip().lower()

        if not email:
            messages.error(request, 'El correo es obligatorio.')
            return render(request, 'usuarios/forgot_password.html', context)

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Ingresa un correo válido.')
            return render(request, 'usuarios/forgot_password.html', context)

        if not User.objects.filter(email=email).exists():
            messages.error(request, 'No existe una cuenta con este correo.')
            return render(request, 'usuarios/forgot_password.html', context)

        # 🔐 Generar código real
        code = random.randint(100000, 999999)

        # Guardar temporalmente
        request.session['reset_code'] = str(code)
        request.session['reset_email'] = email

        # 📩 Enviar correo real
        send_mail(
            'Código de recuperación - SenaMerch',
            f'Tu código de verificación es: {code}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        messages.success(request, 'Te enviamos un código a tu correo.')
        return redirect('code_verify')

    return render(request, 'usuarios/forgot_password.html', context)


# =========================
# VERIFICAR CÓDIGO REAL
# =========================

def code_verify_view(request):
    if request.method == 'POST':
        code_entered = request.POST.get('code', '').strip()
        real_code = request.session.get('reset_code')

        if not code_entered:
            messages.error(request, 'Debes ingresar el código completo.')
            return redirect('code_verify')

        if not code_entered.isdigit() or len(code_entered) != 6:
            messages.error(request, 'El código debe ser de 6 números.')
            return redirect('code_verify')

        if not real_code:
            messages.error(request, 'El código expiró. Solicita uno nuevo.')
            return redirect('forgot_password')

        if code_entered != real_code:
            messages.error(request, 'Código incorrecto.')
            return redirect('code_verify')

        return redirect('reset_password')

    return render(request, 'usuarios/code_verify.html')


# =========================
# RESTABLECER CONTRASEÑA REAL
# =========================

def reset_password_view(request):
    if request.method == 'POST':
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not password or not password_confirm:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('reset_password')

        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('reset_password')

        # Validación fuerte de seguridad
        if not re.match(
            r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&.#-_]).{8,}$',
            password
        ):
            messages.error(
                request,
                'La contraseña debe tener mínimo 8 caracteres, una mayúscula, un número y un símbolo.'
            )
            return redirect('reset_password')

        email = request.session.get('reset_email')

        if not email:
            messages.error(request, 'Sesión expirada. Vuelve a solicitar el código.')
            return redirect('forgot_password')

        user = User.objects.get(email=email)

        user.password = make_password(password)
        user.save()

        request.session.flush()

        messages.success(request, 'Contraseña actualizada correctamente.')
        return redirect('login')

    return render(request, 'usuarios/reset_password.html')



# =========================
# CONTACTO (NO TOCADO)
# =========================

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        query_type = request.POST.get('query_type', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not query_type or not message:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('contact')

        messages.success(request, 'Tu mensaje fue enviado correctamente.')
        return redirect('contact')

    return render(request, 'usuarios/contact.html')
