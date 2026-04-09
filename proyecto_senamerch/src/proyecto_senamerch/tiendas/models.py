from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.text import slugify
from core.models import BaseModel
User = get_user_model()
# ---> Lógica para el Validador de teléfono
phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message="El teléfono debe tener entre 7 y 15 dígitos."
)
class Tienda(BaseModel):
    # ---> Opciones de categorías
    CATEGORIA_CHOICES = [
        ("frutas", "Frutas"),
        ("verduras", "Verduras"),
        ("carnes", "Carnes"),
        ("bebidas", "Bebidas"),
        ("lacteos", "Lácteos"),
        ("granos", "Granos"),
        ("cereales", "Cereales"),
        ("oleaginosas", "Oleaginosas"),
        ("ornamentales", "Ornamentales"),
        ("otros", "Otros"),
    ]
    propietario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tiendas"
    )
    nombre = models.CharField(
        max_length=120,
        unique=True
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        null=True
    )
    email = models.EmailField(
        unique=True
    )
    telefono = models.CharField(
        max_length=15,
        validators=[phone_validator]
    )
    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIA_CHOICES,
        default="otros"
    )
    descripcion = models.TextField(blank=True)
    # ---> Lógica para las IMÁGENES
    logo = models.ImageField(
        upload_to="tiendas/logos/",
        blank=True,
        null=True
    )
    imagen_portada = models.ImageField(
        upload_to="tiendas/portadas/",
        blank=True,
        null=True
    )
    # ---> Lógica para la DIRECCIÓN
    barrio = models.CharField(max_length=120, blank=True)
    numero_direccion = models.CharField(max_length=100, blank=True)
    tipo_via = models.CharField(max_length=100, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    municipio = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=20, blank=True)
    informacion_adicional = models.TextField(blank=True)
    # ---> Lógica para las ESTADÍSTICAS DE LAS CALIFICACIONES.
    rating_promedio = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0
    )
    total_productos = models.PositiveIntegerField(default=0)
    # ---> Lógica para un NUEVO CAMPO ACTIVO
    activo = models.BooleanField(default=True)  # ---> Este es el campo que se agregará.
    # ---> Lógica que Define nombres visibles, orden por fecha y optimización de búsquedas.
    class Meta:
        verbose_name = "Tienda"
        verbose_name_plural = "Tiendas"
        ordering = ["-creado_en"]  # ---> BaseModel
        indexes = [
            models.Index(fields=["nombre"]),
            models.Index(fields=["categoria"]),
            models.Index(fields=["activo"]),  # ---> Ahora tenemos el índice para 'activo'
        ]
    # ---> Lógica de MÉTODOS
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            contador = 1
            while Tienda.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{contador}"
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)
    @property
    def total_productos_activos(self):
        return self.productos.filter(activo=True).count()

    def __str__(self):
        return f"{self.nombre} ({self.propietario.username})"