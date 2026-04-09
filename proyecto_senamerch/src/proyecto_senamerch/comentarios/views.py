from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from productos.models import Producto
from .models import Comentario
import json
# ---> lógica para crear un comentario.
@login_required
def crear_comentario(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            texto = data.get("texto", "").strip()
            if not texto:
                return JsonResponse({"success": False, "error": "Comentario vacío"}, status=400)
            comentario = Comentario.objects.create(
                producto=producto,
                usuario=request.user,
                texto=texto
            )
            return JsonResponse({
                "success": True,
                "id": comentario.id,
                "usuario": request.user.username,
                "texto": comentario.texto,
                "fecha": comentario.creado_en.strftime("%d/%m/%Y %H:%M"),
                "es_mio": True
            })
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Error de datos"}, status=400)
# ---> Lógica para obtener comentarios.
def obtener_comentarios(request, id):
    comentarios = Comentario.objects.filter(
        producto_id=id
    ).select_related("usuario").order_by("-creado_en")
    data = []
    for c in comentarios:
        data.append({
            "id": c.id,
            "usuario": c.usuario.username,
            "texto": c.texto,
            "fecha": c.creado_en.strftime("%d/%m/%Y %H:%M"),
            "es_mio": request.user.is_authenticated and c.usuario == request.user
        })
    return JsonResponse(data, safe=False)
# ---> Lógica para eliminar comentario.
@login_required
def eliminar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)
    if comentario.usuario != request.user:
        return JsonResponse({"success": False, "error": "No autorizado"}, status=403)
    comentario.delete()
    return JsonResponse({
        "success": True
    })
# ---> Lógica para editar comentario.
@login_required
def editar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)
    if comentario.usuario != request.user:
        return JsonResponse({"success": False, "error": "No autorizado"}, status=403)
    try:
        data = json.loads(request.body)
        texto = data.get("texto", "").strip()
        if not texto:
            return JsonResponse({"success": False, "error": "Comentario vacío"}, status=400)
        comentario.texto = texto
        comentario.save()
        return JsonResponse({
            "success": True,
            "texto": comentario.texto
        })
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Error de datos"}, status=400)