from django.db import models
from django.utils import timezone
from tiendas.models import Tienda
from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models import Avg

# ----------------------------
# MODELO PRODUCTO
# ----------------------------
class Producto(models.Model):
    CATEGORIA_CHOICES = [
        ('frutas', 'Frutas'),
        ('verduras', 'Verduras'),
        ('carnes', 'Carnes'),
        ('bebidas', 'Bebidas'),
        ('otros', 'Otros'),
        ('lacteos', 'Lácteos'),
        ('granos', 'Granos'),
        ('ornamentales', 'Ornamentales'),
        ('cereales', 'Cereales'),
        ('oleaginosas', 'Oleaginosas'),
    ]

    UNIDAD_MEDIDA_CHOICES = [
        ('kg', 'Kilogramos'),
        ('lb', 'Libras'),
        ('unidad', 'Unidad'),
        ('litro', 'Litros'),
        ('mililitro', 'Mililitros'),
    ]

    TIPO_PRODUCTO_CHOICES = [
        ('solido', 'Sólido'),
        ('liquido', 'Líquido'),
    ]

    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
    ]

    TIPO_ENVIO_CHOICES = [
        ('contraentrega', 'Contraentrega'),
    ]

    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=150)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES, default='otros')
    unidad_medida = models.CharField(max_length=20, choices=UNIDAD_MEDIDA_CHOICES, default='kg')
    tipo_producto = models.CharField(max_length=20, choices=TIPO_PRODUCTO_CHOICES, default='solido')
    descuento = models.PositiveIntegerField(default=0, help_text="Porcentaje de descuento")
    fecha_caducidad = models.DateField(default=timezone.now)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='efectivo')
    tipo_envio = models.CharField(max_length=20, choices=TIPO_ENVIO_CHOICES, default='contraentrega')
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock disponible", help_text="Cantidad actual disponible para la venta")
    stock_minimo = models.PositiveIntegerField(default=0, verbose_name="Stock mínimo", help_text="Nivel mínimo antes de mostrar alerta")
    descripcion = models.TextField()
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.tienda.nombre}"

    @property
    def precio_con_descuento(self):
        if self.descuento > 0:
            descuento = (self.precio * Decimal(self.descuento)) / Decimal(100)
            return self.precio - descuento
        return self.precio

    @property
    def imagen_principal(self):
        primera_imagen = self.imagenes.first()
        if primera_imagen and primera_imagen.imagen:
            return primera_imagen.imagen.url
        return "/static/assets/img/default-product.jpg"

    @property
    def rating_promedio(self):
        promedio = self.calificaciones.aggregate(promedio=Avg("puntuacion"))
        return round(promedio["promedio"] or 0, 1)

    @property
    def total_calificaciones(self):
        return self.calificaciones.count()


# ----------------------------
# IMÁGENES DEL PRODUCTO
# ----------------------------
class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/')

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"


# ----------------------------
# CALIFICACIONES
# ----------------------------
class Calificacion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="calificaciones")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    puntuacion = models.PositiveIntegerField(choices=[(1, "1 estrella"), (2, "2 estrellas"), (3, "3 estrellas"), (4, "4 estrellas"), (5, "5 estrellas")])
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("producto", "usuario")
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.usuario.username} calificó {self.producto.nombre} con {self.puntuacion}"


# ----------------------------
# COMENTARIOS DEL PRODUCTO
# ----------------------------
class Comentario(models.Model):
    producto = models.ForeignKey(Producto, related_name="comentarios_producto", on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.usuario.username} comentó en {self.producto.nombre}"