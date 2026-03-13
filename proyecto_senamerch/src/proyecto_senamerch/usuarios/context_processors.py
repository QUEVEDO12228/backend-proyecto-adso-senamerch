from tiendas.models import Tienda

def es_vendedor_context(request):
    """
    Detecta si el usuario autenticado es propietario de alguna tienda.
    Retorna {'es_vendedor': True/False} para todos los templates.
    """
    es_vendedor = False
    if request.user.is_authenticated:
        es_vendedor = Tienda.objects.filter(propietario=request.user).exists()
    return {"es_vendedor": es_vendedor}