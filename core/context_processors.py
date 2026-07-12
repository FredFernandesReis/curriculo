"""Context processors globais."""
from django.conf import settings


def site_settings(request):
    """WhatsApp global, ou do vendedor da sessão (/p/slug/)."""
    numero = settings.WHATSAPP_NUMBER
    display = getattr(settings, 'WHATSAPP_DISPLAY', settings.WHATSAPP_NUMBER)
    vendedor = None

    vendedor_id = request.session.get('vendedor_id') if hasattr(request, 'session') else None
    if vendedor_id:
        try:
            from accounts.models import Vendedor
            vendedor = Vendedor.objects.filter(pk=vendedor_id, ativo=True).first()
            if vendedor:
                numero = vendedor.whatsapp_link_number
                display = vendedor.whatsapp_display
        except Exception:
            vendedor = None

    return {
        'WHATSAPP_NUMBER': numero,
        'WHATSAPP_DISPLAY': display,
        'CURRICULO_PRECO': settings.CURRICULO_PRECO,
        'vendedor_sessao': vendedor,
    }
