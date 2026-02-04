# =========================
# IMPORTACIONES
# =========================

import re  
# Librería para usar expresiones regulares
# Sirve para validar formatos como:
# nombres, teléfonos y contraseñas seguras

import random  
# Permite generar números aleatorios
# Aquí se usa para crear el código de recuperación de 6 dígitos

from django.shortcuts import render, redirect  
# render → muestra páginas HTML
# redirect → redirige a otra ruta

from django.contrib import messages  
# Sistema de mensajes de Django para mostrar errores o avisos en pantalla

from django.contrib.auth import authenticate, login  
# authenticate → valida usuario y contraseña
# login → inicia sesión del usuario

from django.contrib.auth.models import User  
# Modelo de usuarios que viene por defecto en Django
# Representa la tabla de usuarios en la base de datos

from django.core.validators import validate_email  
# Valida que un correo tenga formato correcto

from django.core.exceptions import ValidationError  
# Se usa para capturar errores cuando el correo no es válido

from django.core.mail import send_mail  
# Permite enviar correos electrónicos (códigos de recuperación)

from django.conf import settings  
# Accede a configuraciones del proyecto (correo emisor, etc)

from django.contrib.auth.hashers import make_password  
# Encripta contraseñas antes de guardarlas en la base de datos


# =========================
# LOGIN
# =========================

def login_view(request):
    # Variable que indica si el formulario fue enviado
    context = {'form_submitted': False}

    # Si el usuario envió el formulario
    if request.method == 'POST':
        context['form_submitted'] = True

        # Obtener datos del formulario
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Verificar campos vacíos
        if not email or not password:
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'usuarios/login.html', context)

        # Validar formato de correo
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Ingresa un correo electrónico válido.')
            return render(request, 'usuarios/login.html', context)

        # Autenticar usuario con Django
        user = authenticate(request, username=email, password=password)

        # Si no existe el usuario o la contraseña es incorrecta
        if user is None:
            messages.error(
                request,
                'Correo o contraseña incorrectos. ¿Aún no tienes cuenta? Regístrate.'
            )
            return render(request, 'usuarios/login.html', context)

        # Iniciar sesión
        login(request, user)

        # Redirigir al inicio
        return redirect('home')

    # Mostrar página de login
    return render(request, 'usuarios/login.html', context)


# =========================
# REGISTRO
# =========================

def register_view(request):
    # Si el usuario envió el formulario
    if request.method == 'POST':

        # Obtener datos del formulario
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        # Verificar que todos los campos estén llenos
        if not all([name, phone, email, password, password_confirm]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('register')

        # Validar que el nombre solo tenga letras y mínimo 3 caracteres
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]{3,}$', name):
            messages.error(request, 'El nombre debe tener al menos 3 letras y no números.')
            return redirect('register')

        # Limpiar teléfono (quitar espacios y guiones)
        phone_clean = phone.replace(' ', '').replace('-', '')

        # Validar formato de teléfono colombiano
        if not re.match(r'^(\+57)?[0-9]{10}$', phone_clean):
            messages.error(request, 'Número de teléfono inválido.')
            return redirect('register')

        # Validar correo electrónico
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Correo electrónico inválido.')
            return redirect('register')

        # Verificar si el correo ya está registrado
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
            return redirect('register')

        # Verificar que las contraseñas coincidan
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('register')

        # Validar contraseña segura
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

        # Crear usuario en la base de datos
        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        messages.success(request, 'Cuenta creada correctamente. Inicia sesión.')
        return redirect('login')

    # Mostrar página de registro
    return render(request, 'usuarios/register.html')


# =========================
# REGISTRO PASO 2
# =========================

def register_step_2(request):
    # Muestra el segundo paso del registro
    return render(request, 'usuarios/register2.html')


# =========================
# RECUPERAR CONTRASEÑA
# =========================

def forgot_password_view(request):

    # Controla si el formulario fue enviado
    context = {'form_submitted': False}

    if request.method == 'POST':
        context['form_submitted'] = True

        # Obtener correo
        email = request.POST.get('email', '').strip().lower()

        # Verificar campo vacío
        if not email:
            messages.error(request, 'El correo es obligatorio.')
            return render(request, 'usuarios/forgot_password.html', context)

        # Validar correo
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Ingresa un correo válido.')
            return render(request, 'usuarios/forgot_password.html', context)

        # Verificar que exista el usuario
        if not User.objects.filter(email=email).exists():
            messages.error(request, 'No existe una cuenta con este correo.')
            return render(request, 'usuarios/forgot_password.html', context)

        # Generar código aleatorio de 6 dígitos
        code = random.randint(100000, 999999)

        # Guardar código y correo en sesión temporal
        request.session['reset_code'] = str(code)
        request.session['reset_email'] = email

        # Enviar correo con el código
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
# VERIFICAR CÓDIGO
# =========================

def code_verify_view(request):

    if request.method == 'POST':

        # Obtener código ingresado por el usuario
        code_entered = request.POST.get('code', '').strip()

        # Obtener código real guardado en sesión
        real_code = request.session.get('reset_code')

        # Validar que no esté vacío
        if not code_entered:
            messages.error(request, 'Debes ingresar el código completo.')
            return redirect('code_verify')

        # Validar que sean 6 números
        if not code_entered.isdigit() or len(code_entered) != 6:
            messages.error(request, 'El código debe ser de 6 números.')
            return redirect('code_verify')

        # Validar que exista código en sesión
        if not real_code:
            messages.error(request, 'El código expiró. Solicita uno nuevo.')
            return redirect('forgot_password')

        # Comparar códigos
        if code_entered != real_code:
            messages.error(request, 'Código incorrecto.')
            return redirect('code_verify')

        # Si todo está bien → ir a resetear contraseña
        return redirect('reset_password')

    return render(request, 'usuarios/code_verify.html')


# =========================
# RESTABLECER CONTRASEÑA
# =========================

def reset_password_view(request):

    if request.method == 'POST':

        # Obtener contraseñas
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        # Verificar campos vacíos
        if not password or not password_confirm:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('reset_password')

        # Verificar que coincidan
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('reset_password')

        # Validar contraseña fuerte
        # Se valida que la contraseña cumpla reglas de seguridad fuertes usando una expresión regular
        if not re.match(

            # ^  → indica el inicio del texto (empieza a evaluar desde el primer carácter)
            # (?=.*[A-Z]) → obliga a que exista al menos UNA letra mayúscula
            # (?=.*[a-z]) → obliga a que exista al menos UNA letra minúscula
            # (?=.*\d)    → obliga a que exista al menos UN número (0–9)
            # (?=.*[@$!%*?&.#-_]) → obliga a que exista al menos UN símbolo especial
            # .{8,} → indica que la contraseña debe tener mínimo 8 caracteres en total
            # $ → indica el final del texto (termina de evaluar la contraseña completa)

            r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&.#-_]).{8,}$',

            # password es el texto que se está validando (la contraseña ingresada por el usuario)
            password
        ):

            messages.error(
                request,
                'La contraseña debe tener mínimo 8 caracteres, una mayúscula, un número y un símbolo.'
            )
            return redirect('reset_password')

        # Obtener correo guardado en sesión
        email = request.session.get('reset_email')

        # Validar sesión activa
        if not email:
            messages.error(request, 'Sesión expirada. Vuelve a solicitar el código.')
            return redirect('forgot_password')

        # Obtener usuario
        user = User.objects.get(email=email)

        # Guardar contraseña cifrada
        user.password = make_password(password)
        user.save()

        # Borrar datos temporales
        request.session.flush() # flush() elimina los datos temporales de sesión una vez completado el proceso de recuperación, 
        #evitando reutilización de códigos y mejorando la seguridad.

        messages.success(request, 'Contraseña actualizada correctamente.')
        return redirect('login')

    return render(request, 'usuarios/reset_password.html')


# =========================
# CONTACTO
# =========================

def contact_view(request):

    if request.method == 'POST':

        # Obtener datos del formulario
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        query_type = request.POST.get('query_type', '').strip()
        message = request.POST.get('message', '').strip()

        # Validar campos vacíos
        if not name or not email or not query_type or not message:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('contact')

        messages.success(request, 'Tu mensaje fue enviado correctamente.')
        return redirect('contact')

    return render(request, 'usuarios/contact.html')
