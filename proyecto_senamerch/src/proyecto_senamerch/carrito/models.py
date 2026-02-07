from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto

class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.cantidad * self.producto.precio
