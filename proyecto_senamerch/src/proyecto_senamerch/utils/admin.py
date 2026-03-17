def deshabilitar(modeladmin, request, queryset):
    queryset.update(activo=False)

deshabilitar.short_description = "Deshabilitar seleccionados"


def habilitar(modeladmin, request, queryset):
    queryset.update(activo=True)

habilitar.short_description = "Habilitar seleccionados"