from django.db import models
from django.contrib.auth import get_user_model
from productos.models import Producto
from core.models import BaseModel
from decimal import Decimal
User = get_user_model()
# ---> Lógica de MODELO CARRITO
class Carrito(BaseModel):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='carrito'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"
    def __str__(self):
        return f"Carrito de {self.usuario.username}"
    # ---> Lógica de PROPIEDADES
    @property
    def items_carrito(self):
        return self.items.all()
    def get_total(self):
        """Total SIN descuento"""
        return sum(item.subtotal() for item in self.items.all())
    def get_total_con_descuento(self):
        """Total CON descuento 🔥"""
        return sum(item.subtotal_con_descuento for item in self.items.all())
    def total_items(self):
        """Cantidad total de productos"""
        return sum(item.cantidad for item in self.items.all())
# ---> Lógica del Modelo de ítem del carrito (producto + cantidad)
class ItemCarrito(models.Model):

    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )
    cantidad = models.PositiveIntegerField(default=1)
    class Meta:
        unique_together = ("carrito", "producto")
        verbose_name = "Item de Carrito"
        verbose_name_plural = "Items de Carrito"
    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

    # ---> Lógica de CÁLCULOS
    def subtotal(self):
        return self.cantidad * self.producto.precio
    @property
    def subtotal_con_descuento(self):
        precio = self.producto.precio
        descuento = (precio * Decimal(self.producto.descuento)) / Decimal(100)
        precio_final = precio - descuento
        return precio_final * self.cantidad