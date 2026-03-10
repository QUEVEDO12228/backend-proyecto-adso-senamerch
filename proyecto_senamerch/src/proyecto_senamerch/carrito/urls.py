# carrito/urls.py
from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('', views.shopping_cart, name='shopping_cart'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar/<int:item_id>/', views.eliminar_producto, name='eliminar_producto'),
]