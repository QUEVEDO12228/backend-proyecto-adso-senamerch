from django.urls import path
from . import views
from usuarios.views import home_view

urlpatterns = [

    # 👉 PRIMERA RUTA = HOME
    path('', home_view, name='home'),

    # LOGIN
    path('login/', views.login_view, name='login'),

    # REGISTRO
    path('register/', views.register_view, name='register'),
    path('register2/', views.register_step_2, name='register2'),

    # ADDRESS
    path('add-address/', views.add_address_view, name='add_address'),
    path('add-address-2/', views.add_address_step_2, name='add_address2'),

    # OTROS
    path('contact/', views.contact_view, name='contact'),
    
]

    