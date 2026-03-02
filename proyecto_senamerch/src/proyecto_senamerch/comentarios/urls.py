from django.urls import path
from . import views

app_name = "comentarios"

urlpatterns = [
    path('crear/<int:id>/', views.crear_comentario, name='crear_comentario'),
    path('obtener/<int:id>/', views.obtener_comentarios, name='obtener_comentarios'),
]