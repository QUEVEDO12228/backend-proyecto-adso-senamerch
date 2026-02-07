from django.db import models
from django.contrib.auth.models import User

class Tienda(models.Model):
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tiendas')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
