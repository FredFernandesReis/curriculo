"""Permissões do painel."""
from accounts.utils import get_vendedor, vendedor_ativo


def pode_acessar_painel(user):
    """Superuser, staff ou vendedor ativo."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return vendedor_ativo(user)


def is_admin(user):
    """Compat: mesmo critério do painel."""
    return pode_acessar_painel(user)


def pode_excluir_curriculo(user):
    """Apenas superusuários podem excluir currículos."""
    return user.is_authenticated and user.is_superuser


def pode_ver_todos(user):
    """Somente superusuário vê currículos de todos os parceiros."""
    return user.is_authenticated and user.is_superuser


def curriculos_do_usuario(user):
    """Queryset filtrado: todos (admin) ou só do vendedor."""
    from curriculos.models import Curriculo
    qs = Curriculo.objects.select_related('cliente', 'vendedor')
    if pode_ver_todos(user):
        return qs
    v = get_vendedor(user)
    if v:
        return qs.filter(vendedor=v)
    return qs.none()


def curriculo_do_usuario(user, pk):
    """Retorna currículo se o usuário puder acessá-lo."""
    return curriculos_do_usuario(user).filter(pk=pk).first()


def curriculo_pode_ter_pdf(curriculo):
    """PDF só existe para currículos pagos ou enviados."""
    return curriculo.status in ('pago', 'enviado')
