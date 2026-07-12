"""Login e perfil do parceiro (vendedor)."""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.forms import PerfilVendedorForm
from accounts.utils import get_vendedor, vendedor_ativo
from dashboard.permissions import pode_acessar_painel


def parceiro_login(request):
    """Login da área do parceiro."""
    if request.user.is_authenticated and pode_acessar_painel(request.user):
        return redirect('dashboard:home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and pode_acessar_painel(user):
            login(request, user)
            return redirect('dashboard:home')
        messages.error(
            request,
            'Credenciais inválidas ou conta sem permissão. Peça acesso ao administrador.',
        )

    return render(request, 'accounts/login.html')


def parceiro_logout(request):
    logout(request)
    return redirect('accounts:login')


@login_required(login_url='accounts:login')
def parceiro_perfil(request):
    """Editar dados públicos e copiar link da página."""
    if not pode_acessar_painel(request.user):
        messages.error(request, 'Sem permissão.')
        return redirect('accounts:login')

    vendedor = get_vendedor(request.user)
    if not vendedor and not request.user.is_superuser:
        messages.error(request, 'Perfil de vendedor não encontrado.')
        return redirect('dashboard:home')

    # Superuser sem perfil: só redireciona
    if not vendedor:
        messages.info(request, 'Superusuário gerencia vendedores em /admin/.')
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = PerfilVendedorForm(request.POST, instance=vendedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado!')
            return redirect('accounts:perfil')
    else:
        form = PerfilVendedorForm(instance=vendedor)

    link = request.build_absolute_uri(vendedor.get_public_path())
    return render(request, 'accounts/perfil.html', {
        'form': form,
        'vendedor': vendedor,
        'link_publico': link,
    })
