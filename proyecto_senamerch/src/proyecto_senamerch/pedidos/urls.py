# pedidos/urls.py
from django.urls import path
from . import views

app_name = "pedidos"

urlpatterns = [
    # Listado de pedidos del cliente (pendientes, entregados, cancelados)
    path("client/orders/", views.client_orders, name="client_orders"),
    path('cancel/<int:pedido_id>/', views.cancel_order, name='cancel_order'),
    path('edit/<int:pedido_id>/', views.edit_order, name='edit_order'),
    # Vista de detalle de compra entregada
    path("purchases/<int:pedido_id>/", views.view_purchase, name="view_purchase"),
    path("buy-cart/", views.buy_cart, name="buy_cart"), 
    path("payment-method/", views.option_payment_method, name="payment_method"),
]