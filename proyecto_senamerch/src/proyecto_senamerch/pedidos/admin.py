from django.contrib import admin
from .models import Pedido, PedidoItem
from utils.admin import deshabilitar, habilitar


class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 0
    readonly_fields = ("producto", "cantidad", "precio_unitario")


def marcar_entregado(modeladmin, request, queryset):
    queryset.update(estado="delivered")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "estado", "total", "activo", "creado_en")
    list_filter = ("estado", "activo", "creado_en")
    search_fields = ("usuario__username",)

    readonly_fields = ("creado_en",)
    inlines = [PedidoItemInline]

    actions = [deshabilitar, habilitar, marcar_entregado]

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(activo=True)