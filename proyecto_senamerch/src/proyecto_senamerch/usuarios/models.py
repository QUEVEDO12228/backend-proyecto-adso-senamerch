from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=20, blank=True)
    image = models.ImageField(
        upload_to='profiles/',
        default='profiles/default.png',
        blank=True
    )

    # Dirección
    neighborhood = models.CharField(max_length=100, blank=True)
    address_number = models.CharField(max_length=50, blank=True)
    road_type = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    extra_info = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses'
    )

    neighborhood = models.CharField(max_length=100)
    address_number = models.CharField(max_length=50)
    road_type = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    extra_info = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dirección de {self.user.username}"
