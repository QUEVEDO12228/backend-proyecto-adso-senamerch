from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = "tiendas"

urlpatterns = [
    path('home-seller/', views.home_seller, name='home_seller'),
    # =================================
    # CREAR TIENDA
    # =================================
    path('create-store/', views.create_store_view, name='create_store'),
    path('create-store/step-2/', views.create_store2, name='create_store2'),

    # =================================
    # DIRECCIÓN TIENDA
    # =================================
    path('store/add-address/', views.add_address_store, name='add_address_store'),
    path('store/add-address/step-2/', views.add_address_store2, name='add_address_store2'),
    path(
        'perfil-vendedor/',
        views.profile_store_seller,
        name='profile_store_seller'
    ),
    path('orders/', views.store_orders, name='store_orders'),

    path('catalogo/', views.seller_catalog, name='seller_catalog'),
    path('producto/<int:id>/', views.view_description_product_seller, name='view_description_product_seller'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)