from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto
from tiendas.models import Tienda

class Pedido(models.Model):
    ESTADOS_PEDIDO = [
        ('pending', 'Pendiente'),
        ('delivered', 'Entregado'),
        ('canceled', 'Cancelado'),
    ]
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='pending')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} - {self.estado}"


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Pedido #{self.pedido.id}"