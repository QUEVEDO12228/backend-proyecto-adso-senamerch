# Create your views here.
# pedidos/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

pedidos_ejemplo = [
    # tus pedidos...
]

@login_required
def client_orders(request):
    context = {"pedidos": pedidos_ejemplo}
    return render(request, "pedidos/client_orders.html", context)

@login_required
def view_purchases(request):
    entregados = [p for p in pedidos_ejemplo if p["estado"] == "delivered"]
    context = {"pedidos": entregados}
    return render(request, "pedidos/view_purchases.html", context)

def client_orders_view(request):
    return render(request, 'pedidos/client_orders.html')