from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto

class Comentario(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="comentarios"  # Esto está bien ahora que solo hay 1 Comentario
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comentarios")
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.producto.nombre}"