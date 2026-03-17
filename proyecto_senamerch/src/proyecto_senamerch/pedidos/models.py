from django.db import models
from django.contrib.auth import get_user_model
from productos.models import Producto
from tiendas.models import Tienda
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from core.models import BaseModel

User = get_user_model()


# ----------------------------
# MODELO PEDIDO
# ----------------------------
class Pedido(BaseModel):

    ESTADOS_PEDIDO = [
        ('pending', 'Pendiente'),
        ('delivered', 'Entregado'),
        ('canceled', 'Cancelado'),
    ]

    TIPOS_ENTREGA = [
        ('domicilio', 'Domicilio'),
        ('recoger', 'Recoger en tienda'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='pedidos')

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='pending')
    tipo_entrega = models.CharField(max_length=20, choices=TIPOS_ENTREGA, default='domicilio')

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} - {self.estado}"

    # ----------------------------
    # LÓGICA
    # ----------------------------

    @property
    def puede_editar(self):
        """Se puede editar dentro de 2 horas"""
        return (
            self.estado == 'pending' and
            (timezone.now() - self.creado_en).total_seconds() < 7200
        )

    @property
    def debe_cancelarse(self):
        """Se cancela automáticamente después de 6 horas"""
        return timezone.now() >= self.creado_en + timedelta(hours=6)

    def cancelar_si_expirado(self):
        if self.estado == "pending" and self.debe_cancelarse:
            self.estado = "canceled"
            self.save()

    def tiempo_restante_cancelacion(self):
        if self.estado == 'pending':
            tiempo = self.creado_en + timedelta(hours=6) - timezone.now()
            return max(0, tiempo.total_seconds())
        return 0

    def tiempo_restante_cancelacion_formateado(self):
        if self.estado == 'pending':
            tiempo = self.creado_en + timedelta(hours=6) - timezone.now()
            if tiempo > timedelta():
                horas = tiempo.seconds // 3600
                minutos = (tiempo.seconds % 3600) // 60
                return f"{horas}h {minutos}m"
            return "Cancelado automáticamente"
        return None

    def calcular_total(self):
        """Recalcula el total del pedido"""
        total = sum(item.subtotal_con_descuento for item in self.items.all())
        self.total = total
        self.save()


# ----------------------------
# ITEMS DEL PEDIDO
# ----------------------------
class PedidoItem(models.Model):

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Item de Pedido"
        verbose_name_plural = "Items de Pedido"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    # ----------------------------
    # CÁLCULOS
    # ----------------------------

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    @property
    def subtotal_con_descuento(self):
        precio = self.producto.precio
        descuento = (precio * Decimal(self.producto.descuento)) / Decimal(100)
        precio_final = precio - descuento
        return precio_final * self.cantidad


# ----------------------------
# DIRECCIÓN DEL PEDIDO
# ----------------------------
class AddressPedido(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direcciones_pedido')

    neighborhood = models.CharField(max_length=100)
    address_number = models.CharField(max_length=50)
    road_type = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    department = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    extra_info = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dirección de Pedido"
        verbose_name_plural = "Direcciones de Pedido"

    def __str__(self):
        return f"{self.user.username} - {self.city}"