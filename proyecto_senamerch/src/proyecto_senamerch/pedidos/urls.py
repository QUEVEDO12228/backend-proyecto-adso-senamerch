from django.urls import path
from . import views

app_name = "pedidos"

urlpatterns = [

    # ==========================
    # Pedidos del cliente
    # ==========================
    path("client/orders/", views.client_orders, name="client_orders"),
    path("cancel/<int:pedido_id>/", views.cancel_order, name="cancel_order"),

    # ==========================
    # Acciones relacionadas con compras
    # ==========================
    path("editar/<int:pedido_id>/", views.edit_order, name="edit_order"),
    path("purchase_detail/<int:pedido_id>/", views.view_purchase, name="view_purchase"),
    path("buy-cart/", views.buy_cart, name="buy_cart"),
    path("payment-method/", views.option_payment_method, name="payment_method"),

    # ==========================
    # Pedidos de la tienda
    # ==========================
    # Lista de pedidos
    path("orders/", views.store_orders, name="store_orders"),
    
    # Detalle de un pedido
    path("orders/<int:pedido_id>/", views.store_order_detail, name="store_order_detail"),
    
    # Cancelar o entregar pedido desde la tienda
    path("orders/<int:pedido_id>/cancel/", views.cancel_order_store, name="cancel_order_store"),
    path("orders/<int:pedido_id>/deliver/", views.deliver_order_store, name="deliver_order_store"),
    
    # Actualizar estado de pedido (opcional si lo usas)
    path("orders/update-status/<int:pedido_id>/", views.update_order_status, name="update_order_status"),
]