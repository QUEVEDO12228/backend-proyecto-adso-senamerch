from django.contrib import admin
from .models import Tienda
from utils.admin import deshabilitar, habilitar


@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "propietario",
        "categoria",
        "activo",
        "rating_promedio",
        "creado_en"
    )

    search_fields = (
        "nombre",
        "propietario__username",
        "categoria"
    )

    list_filter = (
        "activo",
        "categoria",
        "creado_en"
    )

    readonly_fields = (
        "creado_en",
        "actualizado_en",
        "rating_promedio"
    )

    actions = [deshabilitar, habilitar]

    prepopulated_fields = {"slug": ("nombre",)}

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(activo=True)