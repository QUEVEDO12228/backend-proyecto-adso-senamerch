from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, Address
from utils.admin import deshabilitar, habilitar

User = get_user_model()


# ----------------------------
# INLINE PROFILE (PRO 🔥)
# ----------------------------
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


# ----------------------------
# USER ADMIN PERSONALIZADO
# ----------------------------
class CustomUserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]


# ❗ IMPORTANTE: desregistrar primero
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ----------------------------
# PROFILE ADMIN
# ----------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "city", "activo", "creado_en")
    search_fields = ("user__username", "phone", "city")
    list_filter = ("activo", "city")

    actions = [deshabilitar, habilitar]

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ----------------------------
# ADDRESS ADMIN
# ----------------------------
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "neighborhood", "activo", "creado_en")
    search_fields = ("user__username", "city")
    list_filter = ("activo", "city")

    actions = [deshabilitar, habilitar]

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser