from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from productos.models import Producto
from .models import Comentario
import json

# ===============================
# Crear comentario (AJAX)
# ===============================
@login_required
def crear_comentario(request, id):
    producto = get_object_or_404(Producto, id=id)

    # Manejo AJAX
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            texto = data.get("texto", "").strip()  # <- debe coincidir con tu JS
            if texto:
                comentario = Comentario.objects.create(
                    producto=producto,
                    usuario=request.user,
                    texto=texto
                )
                # Respuesta JSON
                return JsonResponse({
                    "success": True,
                    "usuario": request.user.username,
                    "texto": comentario.texto,
                    "fecha": comentario.creado_en.strftime("%d/%m/%Y %H:%M")
                })
            else:
                return JsonResponse({"success": False, "error": "Comentario vacío"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Error de datos"}, status=400)
    
    # Fallback para formulario normal (no AJAX)
    if request.method == "POST":
        texto = request.POST.get("texto")  # <- también debe coincidir
        if texto:
            Comentario.objects.create(producto=producto, usuario=request.user, texto=texto)
        return redirect(request.META.get('HTTP_REFERER', '/'))

# ===============================
# Obtener comentarios existentes
# ===============================
def obtener_comentarios(request, id):
    comentarios = Comentario.objects.filter(producto_id=id).select_related("usuario").order_by("-creado_en")
    data = [
        {
            "usuario": c.usuario.username,
            "texto": c.texto,
            "fecha": c.creado_en.strftime("%d/%m/%Y %H:%M")
        }
        for c in comentarios
    ]
    return JsonResponse(data, safe=False)