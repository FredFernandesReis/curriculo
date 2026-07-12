"""Helpers de acesso a vendedor."""
from django.core.exceptions import ObjectDoesNotExist

from accounts.models import Vendedor


def get_vendedor(user):
    """Retorna o perfil Vendedor do usuário, se existir."""
    if not user or not user.is_authenticated:
        return None
    try:
        return user.vendedor
    except (ObjectDoesNotExist, AttributeError):
        return None


def vendedor_ativo(user):
    v = get_vendedor(user)
    return bool(v and v.ativo)
