from django.contrib import admin
from .models import Producto, ImagenProducto, Calificacion
from utils.admin import deshabilitar, habilitar


class ImagenInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "tienda", "stock", "activo", "creado_en")
    list_filter = ("activo", "categoria", "tienda")
    search_fields = ("nombre", "tienda__nombre")

    inlines = [ImagenInline]
    actions = [deshabilitar, habilitar]

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(activo=True)


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ("producto", "usuario", "puntuacion", "creado_en")
    list_filter = ("puntuacion",)
