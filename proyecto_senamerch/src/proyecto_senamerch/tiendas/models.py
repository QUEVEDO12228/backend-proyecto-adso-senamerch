from django.db import models
from django.contrib.auth.models import User

class Tienda(models.Model):

    propietario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tiendas'
    )

    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)

    categoria = models.CharField(max_length=50)

    descripcion = models.TextField(blank=True)

    imagen_portada = models.ImageField(
        upload_to='tiendas/',
        blank=True,
        null=True
    )

    creada_en = models.DateTimeField(auto_now_add=True)

    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
