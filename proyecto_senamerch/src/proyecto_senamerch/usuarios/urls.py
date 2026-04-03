from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
# Definir el nombre del espacio de nombres para las URLs de la aplicación 'usuarios'
app_name = "usuarios"
# Importar las vistas que se utilizarán para las rutas de URL
from .views import (
    home_view,
    home_client_view,
    login_view,
    register_view,
    register_step_2,
    reset_password_view,
    add_address_view,
    add_address_step_2,
    contact_view,
    forgot_password_view,
    code_verify_view,
    profile_view,
    logout_view,
    edit_profile_client,
    edit_profile_client2,
    edit_address_profile_user,
    edit_address_profile_user2,
    check_email,
)
# Definición de las rutas URL para la aplicación 'usuarios'
urlpatterns = [
    # =========================
    # VISTAS PÚBLICAS
    # =========================
    path('', home_view, name='home'),  # Página principal (público)
    # =========================
    # AUTENTICACIÓN
    # =========================
    path('login/', login_view, name='login'),  # Vista de inicio de sesión
    path('logout/', logout_view, name='logout'),  # Vista de cierre de sesión
    # =========================
    # Registro
    # =========================
    path('register/', register_view, name='register'),  # Paso 1 de registro
    path('register/step-2/', register_step_2, name='register_step_2'),  # Paso 2 de registro
    # =========================
    # RECUPERACIÓN DE CONTRASEÑA
    # =========================
    path('forgot-password/', forgot_password_view, name='forgot_password'),  # Vista para recuperar contraseña
    path('verify-code/', code_verify_view, name='code_verify'),  # Vista para verificar código de recuperación
    path('reset-password/', reset_password_view, name='reset_password'),  # Vista para restablecer contraseña
    # =========================
    # DIRECCIÓN CLIENTE
    # =========================
    path('add-address/', add_address_view, name='add_address'),  # Vista para agregar dirección
    path('add-address/step-2/', add_address_step_2, name='add_address_step_2'),  # Paso 2 de dirección
    # =========================
    # CONTACTO
    # =========================
    path('contact/', contact_view, name='contact'),  # Vista de contacto
    # =========================
    # VISTA DEL CLIENTE (HOME)
    # =========================
    path('home/', home_client_view, name='home_client'),  # Vista principal para clientes
    # =========================
    # PERFIL
    # =========================
    path('profile/', profile_view, name='profile'),  # Vista del perfil del cliente
    path('edit-profile/', edit_profile_client, name='edit_profile_client'),  # Editar perfil (Paso 1)
    path('edit-profile-2/', edit_profile_client2, name='edit_profile_client2'),  # Editar perfil (Paso 2)
    # =========================
    # EDITAR DIRECCIÓN DEL CLIENTE
    # =========================
    path('edit-address/', edit_address_profile_user, name='edit_address_profile_user'),  # Editar dirección (Paso 1)
    path('edit-address-step-2/', edit_address_profile_user2, name='edit_address_profile_user2'),  # Editar dirección (Paso 2)
    path('check-email/', check_email, name='check_email'),
]
# Si el proyecto está en modo DEBUG, habilitar el acceso a los archivos de medios
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)