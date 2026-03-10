from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto
from tiendas.models import Tienda
from django.utils import timezone
from datetime import timedelta


class Pedido(models.Model):

    ESTADOS_PEDIDO = [
        ('pending', 'Pendiente'),
        ('delivered', 'Entregado'),
        ('canceled', 'Cancelado'),
    ]

    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='pedidos'
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='pending')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} - {self.estado}"

    @property
    def tienda(self):
        """
        Devuelve la tienda relacionada con los productos de este pedido.
        Asume que todos los productos son de la misma tienda.
        """
        primer_item = self.items.first()
        return primer_item.producto.tienda if primer_item else None

    # ⏱️ tiempo máximo para editar (2h)
    def puede_editar(self):
        return timezone.now() < self.creado_en + timedelta(hours=2)

    # ⏱️ tiempo máximo antes de cancelarse (6h)
    def debe_cancelarse(self):
        return timezone.now() >= self.creado_en + timedelta(hours=6)

    # ⏱️ cancelar automáticamente
    def cancelar_si_expirado(self):
        if self.estado == "pending" and self.debe_cancelarse():
            self.estado = "canceled"
            self.save()

    # ⏱️ segundos restantes para cancelar
    def tiempo_restante_cancelacion(self):
        limite = self.creado_en + timedelta(hours=6)
        restante = (limite - timezone.now()).total_seconds()
        return max(int(restante), 0)


class PedidoItem(models.Model):

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Pedido #{self.pedido.id}"