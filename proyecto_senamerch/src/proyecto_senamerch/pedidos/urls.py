from django.urls import path
from . import views

app_name = "pedidos"

urlpatterns = [
    path("client/orders/", views.client_orders, name="client_orders"),
    path('cancel/<int:pedido_id>/', views.cancel_order, name='cancel_order'),
    path("editar/<int:pedido_id>/", views.edit_order, name="edit_order"),
    path("purchases/<int:pedido_id>/", views.view_purchase, name="view_purchase"),
    path("buy-cart/", views.buy_cart, name="buy_cart"), 
    path("payment-method/", views.option_payment_method, name="payment_method"),
    # ✅ Pedidos de la tienda
    path("orders/", views.store_orders, name="store_orders"),
    # ✅ Endpoint para actualizar estado de un pedido
    path("orders/update-status/<int:pedido_id>/", views.update_order_status, name="update_order_status"),
]