from datetime import date

from django import template

register = template.Library()


@register.filter
def idade_anos(ano_nascimento):
    """Calcula idade aproximada a partir do ano de nascimento."""
    try:
        ano = int(ano_nascimento)
    except (TypeError, ValueError):
        return ''
    return max(0, date.today().year - ano)


@register.filter
def split_bullets(texto):
    """Quebra texto de descrição em itens de lista."""
    if not texto:
        return []
    texto = texto.replace('\r\n', '\n').replace('\r', '\n')
    itens = []
    for bloco in texto.split('\n'):
        bloco = bloco.strip(' •-\t')
        if not bloco:
            continue
        if ';' in bloco and len(bloco) > 40:
            for p in bloco.split(';'):
                p = p.strip(' •-\t')
                if p:
                    itens.append(p)
        else:
            itens.append(bloco)
    return itens or [texto.strip()]
