from .models import Tienda

def tienda_context(request):

    es_vendedor = False
    tienda = None

    if request.user.is_authenticated:
        tienda = Tienda.objects.filter(propietario=request.user).first()
        es_vendedor = tienda is not None

    return {
        'es_vendedor': es_vendedor,
        'mi_tienda': tienda
    }