from django.urls import path
from . import views

app_name = "comentarios"

urlpatterns = [

    path("crear/<int:id>/", views.crear_comentario),
    path("obtener/<int:id>/", views.obtener_comentarios),

    path("eliminar/<int:comentario_id>/", views.eliminar_comentario),
    path("editar/<int:comentario_id>/", views.editar_comentario),

]