from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
# Obtener el modelo de usuario del sistema (generalmente el User de Django)
User = get_user_model()
# Validador de teléfono: Asegura que el teléfono tenga exactamente 10 dígitos
phone_validator = RegexValidator(regex=r'^\d{10}$', message='Teléfono debe tener 10 dígitos.')
class Profile(models.Model):
    """ Este modelo representa el perfil de un usuario, incluyendo su teléfono, imagen de perfil y dirección. También incluye información adicional opcional sobre la dirección del usuario. """
    # Relación uno a uno con el usuario
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Teléfono del usuario, validado para asegurarse de que tenga 10 dígitos
    phone = models.CharField(max_length=10, validators=[phone_validator], blank=True)
    # Imagen de perfil con valor por defecto
    image = models.ImageField(
        upload_to='profiles/',  # Directorio donde se suben las imágenes
        default='profiles/default.png',  # Imagen por defecto
        blank=True
    )
    # Dirección del usuario (opcional)
    neighborhood = models.CharField(max_length=100, blank=True)
    address_number = models.CharField(max_length=50, blank=True)
    road_type = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    extra_info = models.TextField(blank=True)
    # Fecha de creación del perfil (automáticamente se establece al crear el perfil)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"
    def __str__(self):
        return f"{self.user.username} - Perfil"
class Address(models.Model):
    """ Este modelo representa una dirección asociada a un usuario. Un usuario puede tener múltiples direcciones. """
    # Relación con el usuario
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    # Información de la dirección
    neighborhood = models.CharField(max_length=100)
    address_number = models.CharField(max_length=50)
    road_type = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    department = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    extra_info = models.TextField(blank=True, null=True)
    # Fecha de creación de la dirección
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"
    def __str__(self):
        return f"{self.user.username} - {self.city} ({self.neighborhood})"