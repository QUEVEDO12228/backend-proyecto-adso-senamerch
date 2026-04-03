from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms

from .models import Profile, Address
from utils.admin import deshabilitar, habilitar

User = get_user_model()


# ----------------------------
# FORM PERSONALIZADO PROFILE (VALIDACIONES PRO)
# ----------------------------
class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "__all__"

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and not phone.isdigit():
            raise forms.ValidationError("El teléfono debe contener solo números.")
        return phone


# ----------------------------
# INLINE PROFILE
# ----------------------------
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


# ----------------------------
# INLINE ADDRESS
# ----------------------------
class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


# ----------------------------
# USER ADMIN PERSONALIZADO
# ----------------------------
class CustomUserAdmin(BaseUserAdmin):
    inlines = [ProfileInline, AddressInline]

    list_display = ("username", "email", "is_active", "is_staff", "is_superuser")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email")

    ordering = ("username",)

    fieldsets = (
        ("Credenciales", {
            "fields": ("username", "password")
        }),
        ("Información personal", {
            "fields": ("first_name", "last_name", "email")
        }),
        ("Permisos", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Fechas importantes", {
            "fields": ("last_login", "date_joined")
        }),
    )

    readonly_fields = ("last_login", "date_joined")


# ❗ IMPORTANTE: desregistrar primero
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ----------------------------
# PROFILE ADMIN
# ----------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm

    list_display = ("user", "phone", "city", "activo", "creado_en")
    search_fields = ("user__username", "phone", "city")
    list_filter = ("activo", "city")

    actions = [deshabilitar, habilitar]

    readonly_fields = ("creado_en", "actualizado_en")

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ----------------------------
# ADDRESS ADMIN
# ----------------------------
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "neighborhood", "activo", "creado_en")
    search_fields = ("user__username", "city", "neighborhood")
    list_filter = ("activo", "city", "department")

    actions = [deshabilitar, habilitar]

    readonly_fields = ("creado_en", "actualizado_en")

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser