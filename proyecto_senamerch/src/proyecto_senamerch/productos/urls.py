from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "productos"

urlpatterns = [
    path("crear/", views.create_product, name="create_product"),
    path("crear/paso-2/", views.create_product_step2, name="create_product_step2"),
    path("crear/paso-3/", views.create_product_step3, name="create_product_step3"),
    path("crear/paso-4/", views.create_product_step4, name="create_product_step4"),
    path(
    'producto/<int:id>/editar/',
    views.edit_product_seller,
    name='edit_product_seller'
    ),
    # EDITAR PRODUCTO
    path(
        "producto/<int:id>/editar/",
        views.edit_product_seller,
        name="edit_product_seller"
    ),
    path(
        "producto/<int:id>/editar/paso-2/",
        views.edit_product_step2,
        name="edit_product_step2"
    ),
    path(
        "producto/<int:id>/editar/paso-3/",
        views.edit_product_step3,
        name="edit_product_step3"
    ),
    path(
        "producto/<int:id>/editar/paso-4/",
        views.edit_product_step4,
        name="edit_product_step4"
    ),
    path(
        "description-product-seller/<int:id>/",
        views.description_product_seller,
        name="description_product_seller"
    ),
    path(
        "producto/<int:id>/",
        views.description_product_client,
        name="description_product_client"
    ),
    path(
        "producto/<int:id>/comprar/",
        views.buy_product,
        name="buy_product"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)