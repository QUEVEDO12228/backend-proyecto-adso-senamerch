from django.db import models
from django.contrib.auth.models import User


class Carrito(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='carrito'
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name='items'
    )

    # 🔥 IMPORTANTE → usar string para evitar errores de importación
    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.CASCADE
    )

    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.cantidad * self.producto.precio

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"