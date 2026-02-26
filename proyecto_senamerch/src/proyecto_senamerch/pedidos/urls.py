# pedidos/urls.py
from django.urls import path
from . import views
from .views import client_orders_view

app_name = "pedidos"

urlpatterns = [
    path("client/orders/", views.client_orders, name="client_orders"),
    path("purchases/", views.view_purchases, name="view_purchases"),
    path('orders/', client_orders_view, name='client_orders'),
]