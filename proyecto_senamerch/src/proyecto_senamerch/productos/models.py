from django.db import models
from tiendas.models import Tienda

class Producto(models.Model):
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
