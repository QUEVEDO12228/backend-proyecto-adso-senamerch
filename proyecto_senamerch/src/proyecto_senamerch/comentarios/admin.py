from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from .models import Comentario
from utils.admin import deshabilitar, habilitar


class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "producto", "activo", "creado_en")
    search_fields = ("usuario__username", "producto__nombre")
    list_filter = ("activo", "creado_en")
    readonly_fields = ("creado_en",)
    actions = [deshabilitar, habilitar]

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(activo=True)


try:
    admin.site.register(Comentario, ComentarioAdmin)
except AlreadyRegistered:
    pass