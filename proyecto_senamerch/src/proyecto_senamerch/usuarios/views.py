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

from django.shortcuts import render, redirect

from django.contrib.auth import logout

from .models import Profile

from tiendas.models import Tienda
from productos.models import Producto
def home_view(request):

    if request.user.is_authenticated:
        # Si está logueado, excluimos los productos de su propia tienda
        productos = Producto.objects.exclude(
            tienda__propietario=request.user
        ).filter(activo=True)
    else:
        # Si no está logueado, mostramos todos los productos activos
        productos = Producto.objects.filter(activo=True)

    return render(request, "usuarios/cards_home.html", {
        "productos": productos
    })

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
                'Correo o contraseña incorrectos.'
            )
            return render(request, 'usuarios/login.html', context)

        # Login correcto
        login(request, user)

        # Verificar si tiene tienda
        tiene_tienda = Tienda.objects.filter(propietario=user).exists()

        if tiene_tienda:
            return redirect('tiendas:home_seller')   # CAMBIO AQUÍ
        else:
            return redirect('home_client')

    return render(request, 'usuarios/login.html', context)


# =========================
# REGISTRO
# =========================

import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Address


# ======================================
# REGISTRO PASO 1
# ======================================

def register_view(request):

    # 🔥 LIMPIAR SI ENTRA AL REGISTRO NUEVO
    if request.method == 'GET' and not request.GET.get('from_address'):
        request.session.pop('address_full', None)
        request.session.pop('address_step_1', None)
        request.session.pop('register_temp', None)

    data = request.session.get('register_temp', {})

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip().lower()

        # 🔥 GUARDAR SIEMPRE (para no perder datos)
        request.session['register_temp'] = {
            'name': name,
            'phone': phone,
            'email': email
        }
        request.session.modified = True

        # VALIDACIONES
        if not all([name, phone, email]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('register')

        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]{3,}$', name):
            messages.error(request, 'Nombre inválido.')
            return redirect('register')

        phone_clean = phone.replace(' ', '').replace('-', '')
        if not re.match(r'^[0-9]{10}$', phone_clean):
            messages.error(request, 'Teléfono inválido.')
            return redirect('register')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Correo inválido.')
            return redirect('register')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Correo ya registrado.')
            return redirect('register')

        # VALIDAR DIRECCIÓN
        if not request.session.get('address_full'):
            messages.error(request, 'Debes agregar una dirección antes de continuar.')
            return redirect('register')

        # GUARDAR DEFINITIVO
        request.session['register_name'] = name
        request.session['register_phone'] = phone_clean
        request.session['register_email'] = email

        return redirect('register_step_2')

    return render(request, 'usuarios/register.html', {'data': data})


# ======================================
# REGISTRO PASO 2
# ======================================
def register_step_2(request):

    if request.method == 'POST':

        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not password or not confirm_password:
            messages.error(request, 'Debes completar ambos campos.')
            return redirect('register_step_2')

        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('register_step_2')

        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&.#_\-]).{8,}$', password):
            messages.error(
                request,
                'Debe tener mínimo 8 caracteres, mayúscula, minúscula, número y símbolo.'
            )
            return redirect('register_step_2')

        name = request.session.get('register_name')
        email = request.session.get('register_email')
        address = request.session.get('address_full')

        if not name or not email or not address:
            messages.error(request, 'La sesión expiró.')
            return redirect('register')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        Profile.objects.create(
            user=user,
            phone=request.session.get('register_phone', '')
        )

        Address.objects.create(
            user=user,
            neighborhood=address.get('neighborhood'),
            address_number=address.get('address_number'),
            road_type=address.get('road_type'),
            postal_code=address.get('postal_code'),
            department=address.get('department'),
            city=address.get('city'),
            extra_info=address.get('additional_info')
        )

        # LIMPIAR SESIÓN
        request.session.pop('register_name', None)
        request.session.pop('register_email', None)
        request.session.pop('address_full', None)

        # 🔥 AQUÍ ESTÁ EL CAMBIO
        return render(request, 'usuarios/register2.html', {
            'success': True
        })

    return render(request, 'usuarios/register2.html')


# ======================================
# DIRECCIÓN PASO 1
# ======================================

def add_address_view(request):

    if request.method == 'POST':

        neighborhood = request.POST.get('neighborhood', '').strip()
        address_number = request.POST.get('address_number', '').strip()
        road_type = request.POST.get('road_type', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()

        if not neighborhood or not address_number:
            messages.error(request, 'Barrio y dirección obligatorios.')
            return redirect('add_address')

        request.session['address_step_1'] = {
            'neighborhood': neighborhood,
            'address_number': address_number,
            'road_type': road_type,
            'postal_code': postal_code,
        }
        request.session.modified = True

        return redirect('add_address_step_2')

    return render(request, 'usuarios/add_address.html')


# ======================================
# DIRECCIÓN PASO 2
# ======================================

def add_address_step_2(request):

    step_1 = request.session.get('address_step_1')

    if not step_1:
        messages.error(request, 'Debes completar el paso anterior.')
        return redirect('add_address')

    if request.method == 'POST':

        department = request.POST.get('department', '').strip()
        city = request.POST.get('city', '').strip()
        additional_info = request.POST.get('additional_info', '').strip()

        if not department or not city:
            messages.error(request, 'Datos incompletos.')
            return redirect('add_address_step_2')

        request.session['address_full'] = {
            **step_1,
            'department': department,
            'city': city,
            'additional_info': additional_info
        }
        request.session.modified = True

        request.session.pop('address_step_1', None)

        # 🔥 VOLVER SIN BORRAR DATOS
        return redirect('/register?from_address=1')

    return render(request, 'usuarios/add_address2.html')

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

def home_client_view(request):
    products = [
        {
            "name": "Tomates Chonto",
            "price": 4500,
            "discount": 4,
            "image": "tomato_image.png",
            "store_logo": "store_seller.jpg",
            "store_name": "Verduras La Huerta",
        },
        {
            "name": "Papa Pastusa",
            "price": 2300,
            "discount": 6,
            "image": "potato_image.png",
            "store_logo": "store_seller.jpg",
            "store_name": "Campo Andino",
        },
    ]

    return render(request, 'usuarios/home_client.html', {
        'products': products
    })

def client_orders_view(request):
    return render(request, 'pedidos/client_orders.html')

def profile_view(request):

    tiene_tienda = Tienda.objects.filter(propietario=request.user).exists()

    if tiene_tienda:
        return redirect('tiendas:profile_store_seller')

    return render(request, 'usuarios/profile_user.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def edit_profile_client(request):
    if request.method == "POST":
        # Aquí luego guardas email, nombre, imagen, etc
        return redirect('edit_profile_client2')

    return render(request, 'usuarios/edit_profile_client.html')

def edit_profile_client2(request):
    if request.method == "POST":
        # Aquí luego guardas teléfono y contraseña
        return redirect('profile')  # o donde vuelva el usuario

    return render(request, 'usuarios/edit_profile_client2.html')





