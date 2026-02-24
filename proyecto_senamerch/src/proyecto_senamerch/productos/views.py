from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def create_product(request):
    if request.method == "POST":
        return redirect("productos:create_product_step2")

    return render(request, "productos/create_product.html")


@login_required
def create_product_step2(request):
    if request.method == "POST":
        return redirect("productos:create_product_step3")

    return render(request, "productos/create_product2.html")


@login_required
def create_product_step3(request):
    if request.method == "POST":
        return redirect("productos:create_product_step4")

    return render(request, "productos/create_product3.html")


@login_required
def create_product_step4(request):
    if request.method == "POST":
        return redirect("productos:create_product")

    return render(request, "productos/create_product4.html")