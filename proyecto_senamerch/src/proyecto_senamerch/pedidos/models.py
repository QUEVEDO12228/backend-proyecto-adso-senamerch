from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto
from tiendas.models import Tienda  # Asegúrate de importar el modelo Tienda
from django.utils import timezone
from datetime import timedelta

class Pedido(models.Model):
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
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='pending')
    tipo_entrega = models.CharField(max_length=20, choices=TIPOS_ENTREGA, default='domicilio')
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='pedidos', default=1)  # Relación con Tienda
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} - {self.estado}"

    @property
    def get_tienda(self):
        """
        Devuelve la tienda relacionada con los productos de este pedido.
        Asume que todos los productos son de la misma tienda.
        """
        primer_item = self.items.first()
        return primer_item.producto.tienda if primer_item else None

    @property
    def puede_editar(self):
        """Determina si el pedido puede ser editado (2 horas de límite desde su creación)."""
        return self.estado == 'pending' and (timezone.now() - self.creado_en).total_seconds() < 7200

    @property
    def debe_cancelarse(self):
        """Determina si el pedido debe cancelarse automáticamente (6 horas de límite desde su creación)."""
        return timezone.now() >= self.creado_en + timedelta(hours=6)

    def cancelar_si_expirado(self):
        """Cancela automáticamente el pedido si ha pasado más de 6 horas desde su creación y está pendiente."""
        if self.estado == "pending" and self.debe_cancelarse:
            self.estado = "canceled"
            self.save()

    def tiempo_restante_cancelacion(self):
        """Devuelve el tiempo restante en segundos para cancelar el pedido (6 horas de límite)."""
        if self.estado == 'pending':
            # Si el pedido está pendiente, calcula los segundos restantes hasta las 6 horas
            tiempo_restante = self.creado_en + timedelta(hours=6) - timezone.now()
            return max(0, tiempo_restante.total_seconds())  # Asegurarse de que no devuelva un valor negativo
        return 0

    def tiempo_restante_cancelacion_formateado(self):
        """Devuelve el tiempo restante en formato legible (horas y minutos)."""
        if self.estado == 'pending':
            tiempo_restante = self.creado_en + timedelta(hours=6) - timezone.now()
            if tiempo_restante > timedelta():
                horas = tiempo_restante.seconds // 3600
                minutos = (tiempo_restante.seconds % 3600) // 60
                return f"{horas} horas y {minutos} minutos"
            else:
                return "Pedido cancelado automáticamente"
        return None


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        """Calcula el subtotal de este ítem (cantidad * precio unitario)."""
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Pedido #{self.pedido.id}"


# ✅ Nuevo modelo de dirección
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos_addresses')
    neighborhood = models.CharField(max_length=100)
    address_number = models.CharField(max_length=50)
    road_type = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    department = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    extra_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dirección (Pedido)"
        verbose_name_plural = "Direcciones (Pedidos)"

    def __str__(self):
        return f"{self.user.username} - {self.city} ({self.neighborhood})"