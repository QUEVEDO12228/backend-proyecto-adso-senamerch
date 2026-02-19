from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
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
    client_orders_view,
    create_store_view,
    create_store_step_2_view,
    profile_view,
    logout_view,
    edit_profile_client,
    edit_profile_client2,
    add_address_store,
    add_address_store2,
)

urlpatterns = [

    # =========================
    # HOME PÚBLICO
    # =========================
    path('', home_view, name='home'),

    # =========================
    # AUTENTICACIÓN
    # =========================
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('register/', register_view, name='register'),
    path('register/step-2/', register_step_2, name='register_step_2'),

    # =========================
    # RECUPERACIÓN DE CONTRASEÑA
    # =========================
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('verify-code/', code_verify_view, name='code_verify'),
    path('reset-password/', reset_password_view, name='reset_password'),

    # =========================
    # DIRECCIÓN CLIENTE
    # =========================
    path('add-address/', add_address_view, name='add_address'),
    path('add-address/step-2/', add_address_step_2, name='add_address_step_2'),

    # =========================
    # CONTACTO
    # =========================
    path('contact/', contact_view, name='contact'),

    # =========================
    # HOME CLIENTE
    # =========================
    path('home/', home_client_view, name='home_client'),

    # =========================
    # PEDIDOS CLIENTE
    # =========================
    path('orders/', client_orders_view, name='client_orders'),

    # =========================
    # CREAR TIENDA
    # =========================
    path('create-store/', create_store_view, name='create_store'),
    path('create-store/step-2/', create_store_step_2_view, name='create_store_step_2'),

    # =========================
    # PERFIL
    # =========================
    path('profile/', profile_view, name='profile'),
    path('edit-profile/', edit_profile_client, name='edit_profile_client'),
    path('edit-profile-2/', edit_profile_client2, name='edit_profile_client2'),

    # =========================
    # DIRECCIÓN TIENDA
    # =========================
    path('store/add-address/', add_address_store, name='add_address_store'),
    path('store/add-address/step-2/', add_address_store2, name='add_address_store2'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)