"""Serviço de notificações via WhatsApp."""
from urllib.parse import quote


# Mensagens cadastradas do fluxo do currículo
MENSAGENS = {
    'adquirir': (
        'Olá! Acabei de criar meu currículo no sistema e gostaria de adquirir '
        'a versão profissional em PDF. Meu nome é: {nome}.'
    ),
    'entrega': (
        'Olá {nome}! Seu pagamento foi confirmado e seu currículo profissional '
        'está pronto. Em seguida enviaremos o PDF. '
        'Desejamos muito sucesso na sua busca por uma oportunidade!'
    ),
}


def obter_mensagem(chave, **kwargs):
    """Retorna mensagem cadastrada com placeholders preenchidos."""
    modelo = MENSAGENS.get(chave, '')
    try:
        return modelo.format(**kwargs)
    except (KeyError, ValueError):
        return modelo


def gerar_link_whatsapp(numero, mensagem):
    """Gera link do WhatsApp com mensagem pré-formatada."""
    numero_limpo = ''.join(filter(str.isdigit, str(numero)))
    if not numero_limpo.startswith('55'):
        numero_limpo = '55' + numero_limpo
    return f'https://wa.me/{numero_limpo}?text={quote(mensagem)}'


def notificar_pagamento_confirmado(curriculo):
    """
    Gera link WhatsApp para notificar cliente sobre pagamento confirmado.
    Retorna dict com link e mensagem para uso no painel admin.
    """
    cliente = curriculo.cliente
    mensagem = obter_mensagem('entrega', nome=cliente.nome_completo or 'cliente')
    link = gerar_link_whatsapp(cliente.telefone_whatsapp, mensagem)
    return {
        'link': link,
        'mensagem': mensagem,
        'telefone': cliente.telefone_whatsapp,
        'nome': cliente.nome_completo,
    }


def processar_pagamento_confirmado(curriculo):
    """
    Processa confirmação de pagamento:
    1. Gera PDF
    2. Prepara notificação WhatsApp
    Não marca como 'enviado' automaticamente — o vendedor baixa e envia o PDF.
    """
    from pdf_generator.generator import gerar_pdf_curriculo
    from curriculos.models import Curriculo

    curriculo = (
        Curriculo.objects.select_related('cliente')
        .prefetch_related('experiencias', 'cursos')
        .get(pk=curriculo.pk)
    )
    pdf_path = gerar_pdf_curriculo(curriculo)
    curriculo.pdf_arquivo = pdf_path
    curriculo.save(update_fields=['pdf_arquivo'])

    return notificar_pagamento_confirmado(curriculo)
