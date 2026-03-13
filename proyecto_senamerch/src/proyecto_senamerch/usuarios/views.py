# =========================
# IMPORTACIONES
# =========================
import re  # Librería para usar expresiones regulares. Se usa para validar datos como nombres, teléfonos, contraseñas, etc.
import random  # Generación de números aleatorios (por ejemplo, para códigos de recuperación).
from django.shortcuts import render, redirect  # render() para mostrar plantillas HTML, redirect() para redirigir a otras rutas.
from django.contrib import messages  # Sistema de mensajes para mostrar errores y alertas.
from django.contrib.auth import authenticate, login  # authenticate() para validar usuario y contraseña, login() para iniciar sesión.
from django.contrib.auth.models import User  # Modelo de usuario predeterminado de Django.
from django.core.validators import validate_email  # Valida el formato de un correo electrónico.
from django.core.exceptions import ValidationError  # Captura errores de validación (por ejemplo, si el correo no es válido).
from django.core.mail import send_mail  # Permite enviar correos electrónicos (como códigos de recuperación).
from django.conf import settings  # Permite acceder a configuraciones globales del proyecto (por ejemplo, configuraciones de correo).
from django.contrib.auth.hashers import make_password  # Se utiliza para encriptar contraseñas antes de almacenarlas en la base de datos.
from django.contrib.auth import logout  # Permite cerrar la sesión de un usuario.
from .models import Profile  # Importa el modelo Profile para usuarios.
from tiendas.models import Tienda  # Importa el modelo Tienda, usado para representar una tienda de usuario.
from productos.models import Producto  # Modelo Producto para manejar los productos.
from django.contrib.auth.decorators import login_required  # Decorador para proteger vistas que requieren estar logueado.
from .models import Address  # Modelo Address para almacenar direcciones de usuario.
from django.contrib.auth import update_session_auth_hash  # Permite actualizar la sesión después de un cambio de contraseña.
import random
import time
from django.core.validators import validate_email
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
# =========================
# Index SenaMerch
# =========================
def home_view(request):
    """ Vista principal de la página de inicio. Si el usuario está autenticado, excluye los productos de su propia tienda. """
    if request.user.is_authenticated:
        productos = Producto.objects.exclude(tienda__propietario=request.user).filter(activo=True)
    else:
        productos = Producto.objects.filter(activo=True)
    return render(request, "usuarios/cards_home.html", {"productos": productos})
# =========================
# Inicio de Sessión en SenaMerch
# =========================
from django.urls import reverse

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
            messages.error(request, 'Correo o contraseña incorrectos.')
            return render(request, 'usuarios/login.html', context)

        # LOGIN CORRECTO
        # LOGIN CORRECTO
        login(request, user)
        messages.success(request, f'Bienvenido {user.username}')

        # Determinar URL de redirección
        if Tienda.objects.filter(propietario=user).exists():
            redirect_url = reverse('tiendas:home_seller')
        else:
            redirect_url = reverse('usuarios:home_client')

        # Enviamos al template
        context['redirect_url'] = redirect_url

    return render(request, 'usuarios/login.html', context)
# Registro de usuario en SenaMerch (PASO 1)
# ==========================================
def register_view(request):
    """ Vista para el primer paso del registro de un nuevo usuario. Valida datos básicos como nombre, teléfono y correo electrónico. """
    if request.method == 'GET' and not request.GET.get('from_address'):
        # Limpiar datos temporales si no se llega desde una dirección
        request.session.pop('address_full', None)
        request.session.pop('address_step_1', None)
        request.session.pop('register_temp', None)
    data = request.session.get('register_temp', {})
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip().lower()
        # Guardar los datos temporales
        request.session['register_temp'] = {'name': name, 'phone': phone, 'email': email}
        request.session.modified = True
        # Validación de campos
        if not all([name, phone, email]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('usuarios:register')
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]{3,}$', name):
            messages.error(request, 'Nombre inválido.')
            return redirect('usuarios:register')
        phone_clean = phone.replace(' ', '').replace('-', '')
        if not re.match(r'^[0-9]{10}$', phone_clean):
            messages.error(request, 'Teléfono inválido.')
            return redirect('usuarios:register')
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Correo inválido.')
            return redirect('usuarios:register')
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Correo ya registrado.')
            return redirect('usuarios:register')
        # Validar que se haya ingresado una dirección
        if not request.session.get('address_full'):
            messages.error(request, 'Debes agregar una dirección antes de continuar.')
            return redirect('usuarios:register')
        # Guardar los datos definitivos y continuar al siguiente paso
        request.session['register_name'] = name
        request.session['register_phone'] = phone_clean
        request.session['register_email'] = email
        return redirect('usuarios:register_step_2')
    return render(request, 'usuarios/register.html', {'data': data})
# ==========================================
# Registro de usuario en SenaMerch (PASO 2)
# ==========================================
def register_step_2(request):

    if request.method == 'POST':

        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        image = request.FILES.get('cover_image')

        if not password or not confirm_password:
            messages.error(request, 'Debes completar ambos campos.')
            return redirect('usuarios:register_step_2')

        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('usuarios:register_step_2')

        name = request.session.get('register_name')
        email = request.session.get('register_email')
        address = request.session.get('address_full')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        Profile.objects.update_or_create(
            user=user,
            defaults={
                'phone': request.session.get('register_phone', ''),
                'image': image
            }
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

        return render(request, 'usuarios/register2.html', {'success': True})

    # 🔴 IMPORTANTE: siempre debe existir este return
    return render(request, 'usuarios/register2.html')
# ==========================================
#  Añadir Dirección para Registrarse (PASO 1)
# ==========================================
def add_address_view(request):
    """ Vista para el primer paso del formulario de dirección. Recoge los datos básicos de la dirección como barrio, número de dirección, tipo de vía y código postal. """
    if request.method == 'POST':
        # Obtener los campos del formulario
        neighborhood = request.POST.get('neighborhood', '').strip()
        address_number = request.POST.get('address_number', '').strip()
        road_type = request.POST.get('road_type', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        # Validar que los campos necesarios no estén vacíos
        if not neighborhood or not address_number:
            messages.error(request, 'Barrio y dirección obligatorios.')
            return redirect('add_address')
        # Guardar los datos en la sesión temporalmente
        request.session['address_step_1'] = {
            'neighborhood': neighborhood,
            'address_number': address_number,
            'road_type': road_type,
            'postal_code': postal_code,
        }
        request.session.modified = True
        # Redirigir al siguiente paso
        return redirect('usuarios:add_address_step_2')
    return render(request, 'usuarios/add_address.html')
# ==========================================
#  Añadir Dirección para Registrarse (PASO 1)
# ==========================================
def add_address_step_2(request):
    """ Vista para el segundo paso del formulario de dirección. Recoge los datos finales de la dirección como departamento, ciudad y información adicional. """
    step_1 = request.session.get('address_step_1')
    # Verificar que el paso 1 haya sido completado antes de continuar
    if not step_1:
        messages.error(request, 'Debes completar el paso anterior.')
        return redirect('add_address')
    if request.method == 'POST':
        # Obtener los campos del formulario
        department = request.POST.get('department', '').strip()
        city = request.POST.get('city', '').strip()
        additional_info = request.POST.get('additional_info', '').strip()
        # Validar que los campos esenciales no estén vacíos
        if not department or not city:
            messages.error(request, 'Datos incompletos.')
            return redirect('add_address_step_2')
        # Guardar la dirección completa en la sesión
        request.session['address_full'] = {
            **step_1,
            'department': department,
            'city': city,
            'additional_info': additional_info
        }
        request.session.modified = True
        # Limpiar datos del paso 1
        request.session.pop('address_step_1', None)
        # Redirigir a la siguiente etapa sin borrar los datos
        return redirect('/register?from_address=1')
    return render(request, 'usuarios/add_address2.html')
# ===========================================================
#  Recuperar Contraseña Para Iniciar Sessión Ingresar correo
# ===========================================================
def forgot_password_view(request):
    """
    Vista para la recuperación de contraseña.
    Envía un código de verificación de 6 dígitos al correo del usuario.
    """

    context = {'form_submitted': False}

    if request.method == 'POST':

        context['form_submitted'] = True

        # Obtener correo
        email = request.POST.get('email', '').strip().lower()

        if not email:
            messages.error(request, 'El correo es obligatorio.')
            return render(request, 'usuarios/forgot_password.html', context)

        # Validar formato
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Ingresa un correo válido.')
            return render(request, 'usuarios/forgot_password.html', context)

        # Verificar usuario
        if not User.objects.filter(email=email).exists():
            messages.error(request, 'No existe una cuenta con este correo.')
            return render(request, 'usuarios/forgot_password.html', context)

        # Generar código OTP
        code = random.randint(100000, 999999)

        # Guardar en sesión
        request.session['reset_code'] = str(code)
        request.session['reset_email'] = email
        request.session['reset_code_time'] = time.time()

        # Renderizar correo HTML
        html_content = render_to_string(
            'usuarios/reset_code_email.html',
            {'code': code}
        )

        # Crear correo
        email_message = EmailMultiAlternatives(
            'Código de recuperación - SenaMerch',
            f'Tu código de verificación es: {code}',
            settings.EMAIL_HOST_USER,
            [email]
        )

        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        messages.success(request, 'Te enviamos un código a tu correo.')

        return redirect('usuarios:code_verify')

    return render(request, 'usuarios/forgot_password.html', context)
# ==========================================================================
#  Recuperar Contraseña Para Iniciar Sessión Ingresar código de verificación
# ==========================================================================
def code_verify_view(request):
    """
    Vista para verificar el código enviado al correo.
    Si es correcto permite restablecer la contraseña.
    """

    if request.method == 'POST':

        code_entered = request.POST.get('code', '').strip()

        real_code = request.session.get('reset_code')
        code_time = request.session.get('reset_code_time')

        # Validar campo vacío
        if not code_entered:
            messages.error(request, 'Debes ingresar el código completo.')
            return redirect('usuarios:code_verify')

        # Validar formato
        if not code_entered.isdigit() or len(code_entered) != 6:
            messages.error(request, 'El código debe ser de 6 números.')
            return redirect('usuarios:code_verify')

        # Verificar existencia del código
        if not real_code or not code_time:
            messages.error(request, 'El código expiró. Solicita uno nuevo.')
            return redirect('usuarios:forgot_password')

        # Verificar expiración (5 minutos)
        if time.time() - code_time > 300:
            messages.error(request, 'El código expiró. Solicita uno nuevo.')
            return redirect('usuarios:forgot_password')

        # Comparar código
        if code_entered != real_code:
            messages.error(request, 'Código incorrecto.')
            return redirect('usuarios:code_verify')

        # Código correcto
        return redirect('usuarios:reset_password')

    return render(request, 'usuarios/code_verify.html')
# =====================================================================
#  Recuperar Contraseña Para Iniciar Sessión Ingresar nueva contraseña
# =====================================================================
def reset_password_view(request):
    """ Vista para restablecer la contraseña del usuario. Recibe y valida las contraseñas nuevas. """
    if request.method == 'POST':
        # Obtener las contraseñas ingresadas por el usuario
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        # Verificar que no haya campos vacíos
        if not password or not password_confirm:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('usuarios:reset_password')
        # Verificar que las contraseñas coincidan
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('usuarios:reset_password')
        # Validar que la contraseña cumpla con las reglas de seguridad
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&.#-_]).{8,}$', password):
            messages.error(request, 'La contraseña debe tener mínimo 8 caracteres, una mayúscula, un número y un símbolo.')
            return redirect('usuarios:reset_password')
        # Obtener el correo guardado en sesión
        email = request.session.get('reset_email')
        # Verificar que la sesión esté activa
        if not email:
            messages.error(request, 'Sesión expirada. Vuelve a solicitar el código.')
            return redirect('usuarios:forgot_password')
        # Obtener el usuario y guardar la nueva contraseña
        user = User.objects.get(email=email)
        user.password = make_password(password)
        user.save()
        # Limpiar datos temporales de sesión
        request.session.flush()
        messages.success(request, 'Contraseña actualizada correctamente.')
        return redirect('usuarios:login')
    return render(request, 'usuarios/reset_password.html')
# ===========================================================
#  Contacto SenaMerch
# ===========================================================
def contact_view(request):
    """ Vista para enviar mensajes de contacto. Los usuarios pueden enviar sus consultas o comentarios. """
    if request.method == 'POST':
        # Obtener los datos del formulario de contacto
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        query_type = request.POST.get('query_type', '').strip()
        message = request.POST.get('message', '').strip()
        # Validar que todos los campos estén completos
        if not name or not email or not query_type or not message:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('contact')
        # Mostrar mensaje de éxito
        messages.success(request, 'Tu mensaje fue enviado correctamente.')
        return redirect('contact')

    return render(request, 'usuarios/contact.html')
# =====================
#  Perfil del cliente 
# =====================
@login_required
def profile_view(request):
    """ Vista para mostrar el perfil del cliente. Muestra la información del usuario y su dirección. """
    profile, created = Profile.objects.get_or_create(user=request.user)
    # Obtener la dirección del usuario
    address = Address.objects.filter(user=request.user).first()
    return render(request, 'usuarios/profile_user.html', {
        'profile': profile,
        'address': address
    })
# ==========================
#  Vuelve A Iniciar Sessión
# ==========================
def logout_view(request):
    """ Vista para cerrar sesión del usuario. """
    logout(request)
    return redirect('usuarios:login')
# =========================================
#  Editar Datos De Perfil Cliente (PASO 1)
# =========================================
@login_required
def edit_profile_client(request):
    """ Vista para editar el perfil del cliente (Paso 1). Permite editar el nombre y correo del usuario, y subir una imagen de perfil. """
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        # Guardar datos temporales en sesión
        request.session['edit_client_data'] = {
            "email": request.POST.get("email"),
            "first_name": request.POST.get("name"),
        }
        # Subir imagen de perfil si se ha seleccionado una
        if request.FILES.get("cover_image"):
            profile.image = request.FILES.get("cover_image")
            profile.save()
        request.session.modified = True
        # Redirigir al paso 2 de la edición
        return redirect('usuarios:edit_profile_client2')
    return render(request, 'usuarios/edit_profile_client.html', {
        "profile": profile
    })
# =========================================
#  Editar Datos De Perfil Cliente (PASO 2)
# =========================================
@login_required
def edit_profile_client2(request):
    """ Vista para guardar los cambios del perfil del cliente (Paso 2). Permite editar el teléfono y la contraseña del usuario. """
    data = request.session.get("edit_client_data")
    if not data:
        return redirect("usuarios:edit_profile_client")
    if request.method == "POST":
        user = request.user
        profile = user.profile
        # Guardar los cambios del usuario
        user.email = data.get("email", user.email)
        user.first_name = data.get("first_name", user.first_name)
        user.save()
        # Guardar el teléfono
        profile.phone = request.POST.get("phone", profile.phone)
        profile.save()
        # Cambio de contraseña si se proporciona
        password = request.POST.get("password")
        confirm = request.POST.get("password_confirm")
        if password and confirm:
            if password != confirm:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect("usuarios:edit_profile_client2")
            user.set_password(password)
            update_session_auth_hash(request, user)
            user.save()
        # Limpiar sesión temporal
        request.session.pop("edit_client_data", None)
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("usuarios:profile")
    return render(request, "usuarios/edit_profile_client2.html", {
        "user": request.user
    })
# ===================================================
#  Editar Datos De Perfil Cliente Dirección (PASO 1)
# ===================================================
@login_required
def edit_address_profile_user(request):
    """ Vista para editar la dirección del cliente (Paso 1). Recoge los datos básicos de la dirección como barrio, número de dirección, tipo de vía y código postal."""
    if request.method == "POST":
        # Guardar datos de la dirección en sesión
        request.session["edit_client_address"] = {
            "neighborhood": request.POST.get("neighborhood"),
            "address_number": request.POST.get("address_number"),
            "road_type": request.POST.get("road_type"),
            "postal_code": request.POST.get("postal_code"),
        }
        return redirect("usuarios:edit_address_profile_user2")
    return render(request, "usuarios/edit_address_profile_client.html")
# ===================================================
#  Editar Datos De Perfil Cliente Dirección (PASO 2)
# ===================================================
@login_required
def edit_address_profile_user2(request):
    """ Vista para guardar los cambios de la dirección del cliente (Paso 2). Recoge los datos finales como departamento, ciudad y información adicional."""
    data = request.session.get("edit_client_address")
    if not data:
        return redirect("usuarios:edit_address_profile_user")
    if request.method == "POST":
        department = request.POST.get("department")
        city = request.POST.get("city")
        extra_info = request.POST.get("extra_info")
        if not department or not city:
            messages.error(request, "Departamento y ciudad son obligatorios.")
            return redirect("usuarios:edit_address_profile_user2")
        # Obtener o crear la dirección sin duplicar
        address, created = Address.objects.get_or_create(user=request.user)
        # Actualizar la dirección del usuario
        address.neighborhood = data.get("neighborhood")
        address.address_number = data.get("address_number")
        address.road_type = data.get("road_type")
        address.postal_code = data.get("postal_code")
        address.department = department
        address.city = city
        address.extra_info = extra_info
        address.save()
        request.session.pop("edit_client_address", None)
        messages.success(request, "Dirección actualizada correctamente.")
        return redirect("usuarios:profile")
    return render(request, "usuarios/edit_address_profile_client2.html")
# ==================================
#  Vista Cliente Al Iniciar Sessión
# ==================================
from productos.models import Producto, Calificacion

def home_client_view(request):

    productos = Producto.objects.select_related(
        'tienda'
    ).prefetch_related('imagenes')

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

    return render(request, "usuarios/card_client.html", {
        "productos": productos
    })