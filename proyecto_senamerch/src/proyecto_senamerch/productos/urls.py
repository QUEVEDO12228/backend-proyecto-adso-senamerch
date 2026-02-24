from django.urls import path
from . import views

app_name = "productos"

urlpatterns = [
    path("crear/", views.create_product, name="create_product"),
    path("crear/paso-2/", views.create_product_step2, name="create_product_step2"),
    path("crear/paso-3/", views.create_product_step3, name="create_product_step3"),
    path("crear/paso-4/", views.create_product_step4, name="create_product_step4"),
]