from django.contrib import admin
from .models import Carrito, ItemCarrito


class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0
    readonly_fields = ("producto", "cantidad")


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):

    list_display = ("usuario", "activo", "creado_en")
    search_fields = ("usuario__username",)

    inlines = [ItemCarritoInline]

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser