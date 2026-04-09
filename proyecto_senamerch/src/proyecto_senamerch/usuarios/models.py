from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from core.models import BaseModel
User = get_user_model()
# ---> Lógica para Validador de teléfono
phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='Teléfono debe tener 10 dígitos.'
)
# ---> Lógica para el MODELO PROFILE.
class Profile(BaseModel):
    """
    Perfil extendido del usuario
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone = models.CharField(
        max_length=10,
        validators=[phone_validator],
        blank=True
    )
    image = models.ImageField(
        upload_to='profiles/',
        default='profiles/default.png',
        blank=True
    )
    # ---> Lógica  Dirección principal
    neighborhood = models.CharField(max_length=100, blank=True)
    address_number = models.CharField(max_length=50, blank=True)
    road_type = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    extra_info = models.TextField(blank=True)
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"
    def __str__(self):
        return f"{self.user.username} - Perfil"
# ---> Lógica para el Modelo Dirección.
class Address(BaseModel):
    """
    Direcciones adicionales del usuario
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    neighborhood = models.CharField(max_length=100)
    address_number = models.CharField(max_length=50)
    road_type = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    department = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    extra_info = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"
    def __str__(self):
        return f"{self.user.username} - {self.city} ({self.neighborhood})"