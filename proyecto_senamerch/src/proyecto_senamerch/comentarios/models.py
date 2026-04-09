from django.db import models
from django.contrib.auth import get_user_model
from productos.models import Producto
from core.models import BaseModel
User = get_user_model()
# ---> Lógica del MODELO COMENTARIO
class Comentario(BaseModel):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="comentarios"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comentarios"
    )
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
    def __str__(self):
        return f"{self.usuario.username} comentó en {self.producto.nombre}"