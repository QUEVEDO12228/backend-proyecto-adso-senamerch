from django.urls import path
from . import views
from usuarios.views import home_view

urlpatterns = [
    path('', home_view, name='home'),

    path('login/', views.login_view, name='login'),

    path('register/', views.register_view, name='register'),
    path('register2/', views.register_step_2, name='register2'),

    path('add-address/', views.add_address_view, name='add_address'),
    path('add-address-2/', views.add_address_step_2, name='add_address2'),

    path('contact/', views.contact_view, name='contact'),

    # 🔑 RECUPERACIÓN DE CONTRASEÑA
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-code/', views.code_verify_view, name='code_verify'),
]
