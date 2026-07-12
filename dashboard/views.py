"""Views do painel administrativo / parceiro."""
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, FileResponse, Http404
from django.db.models import Q, Sum
from django.conf import settings

from curriculos.forms import (
    DadosPessoaisForm, EscolaridadeForm, ExperienciaForm,
    CursoForm, InformacoesExtrasForm,
)
from notifications.whatsapp import processar_pagamento_confirmado
from pdf_generator.generator import gerar_pdf_curriculo
from .permissions import (
    pode_acessar_painel, pode_excluir_curriculo, curriculo_pode_ter_pdf,
    curriculos_do_usuario, curriculo_do_usuario, pode_ver_todos,
)
from accounts.utils import get_vendedor


def admin_login(request):
    """Redireciona para o login unificado do parceiro."""
    return redirect('accounts:login')


def admin_logout(request):
    logout(request)
    return redirect('accounts:login')


@login_required(login_url='accounts:login')
@user_passes_test(pode_acessar_painel, login_url='accounts:login')
def dashboard_home(request):
    """Dashboard com estatísticas (filtradas por vendedor)."""
    qs = curriculos_do_usuario(request.user)
    total = qs.count()
    pagos = qs.filter(status__in=['pago', 'enviado']).count()
    pendentes = qs.filter(status='pendente').count()
    enviados = qs.filter(status='enviado').count()
    valor_arrecadado = qs.filter(
        status__in=['pago', 'enviado']
    ).aggregate(total=Sum('valor_pago'))['total'] or 0

    ultimos = qs.order_by('-criado_em')[:10]
    vendedor = get_vendedor(request.user)
    link_publico = None
    if vendedor:
        link_publico = request.build_absolute_uri(vendedor.get_public_path())

    context = {
        'total': total,
        'pagos': pagos,
        'pendentes': pendentes,
        'enviados': enviados,
        'valor_arrecadado': valor_arrecadado,
        'ultimos': ultimos,
        'preco': settings.CURRICULO_PRECO,
        'pode_excluir': pode_excluir_curriculo(request.user),
        'vendedor': vendedor,
        'ver_todos': pode_ver_todos(request.user),
        'link_publico': link_publico,
    }
    return render(request, 'dashboard/home.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(pode_acessar_painel, login_url='accounts:login')
def lista_solicitacoes(request):
    """Lista solicitações do escopo do usuário."""
    curriculos = curriculos_do_usuario(request.user)

    busca = request.GET.get('busca', '')
    status = request.GET.get('status', '')

    if busca:
        curriculos = curriculos.filter(
            Q(cliente__nome_completo__icontains=busca) |
            Q(cliente__telefone__icontains=busca) |
            Q(cliente__email__icontains=busca)
        )
    if status:
        curriculos = curriculos.filter(status=status)

    from curriculos.models import Curriculo
    return render(request, 'dashboard/lista.html', {
        'curriculos': curriculos,
        'busca': busca,
        'status_filtro': status,
        'status_choices': Curriculo.STATUS_CHOICES,
        'pode_excluir': pode_excluir_curriculo(request.user),
    })


def _get_curriculo_ou_404(request, pk):
    curriculo = curriculo_do_usuario(request.user, pk)
    if not curriculo:
        raise Http404
    return curriculo


@login_required(login_url='accounts:login')
@user_passes_test(pode_acessar_painel, login_url='accounts:login')
def visualizar_curriculo(request, pk):
    from curriculos.models import Curriculo
    curriculo = _get_curriculo_ou_404(request, pk)
    curriculo = (
        type(curriculo).objects.select_related('cliente', 'vendedor')
        .prefetch_related('experiencias', 'cursos')
        .get(pk=curriculo.pk)
    )
    return render(request, 'dashboard/visualizar.html', {
        'curriculo': curriculo,
        'cliente': curriculo.cliente,
        'status_choices': Curriculo.STATUS_CHOICES,
        'pode_excluir': pode_excluir_curriculo(request.user),
        'pode_ver_pdf': curriculo_pode_ter_pdf(curriculo),
    })


def _pdf_existe(curriculo):
    """Verifica se o arquivo PDF existe de verdade no disco/storage."""
    if not curriculo.pdf_arquivo:
        return False
    try:
        return curriculo.pdf_arquivo.storage.exists(curriculo.pdf_arquivo.name)
    except Exception:
        return False


def _garantir_pdf(curriculo):
    """Gera o PDF se ainda não existir ou se o arquivo sumiu do disco."""
    if _pdf_existe(curriculo):
        return curriculo
    # Garante relações carregadas para o gerador
    curriculo = (
        type(curriculo).objects.select_related('cliente')
        .prefetch_related('experiencias', 'cursos')
        .get(pk=curriculo.pk)
    )
    pdf_path = gerar_pdf_curriculo(curriculo)
    curriculo.pdf_arquivo = pdf_path
    curriculo.save(update_fields=['pdf_arquivo'])
    return curriculo


@login_required(login_url='accounts:login')
@user_passes_test(pode_acessar_painel, login_url='accounts:login')
def editar_curriculo(request, pk):
    curriculo = _get_curriculo_ou_404(request, pk)
    curriculo = (
        type(curriculo).objects.select_related('cliente')
        .prefetch_related('experiencias', 'cursos')
        .get(pk=curriculo.pk)
    )

    if request.method == 'POST':
        cliente_form = DadosPessoaisForm(
            request.POST, request.FILES, instance=curriculo.cliente
        )
        escolaridade_form = EscolaridadeForm(request.POST, instance=curriculo)
        extras_form = InformacoesExtrasForm(request.POST, instance=curriculo)

        if cliente_form.is_valid() and escolaridade_form.is_valid() and extras_form.is_valid():
            cliente_form.save()
            escolaridade_form.save()
            extras_form.save()
            messages.success(request, 'Currículo atualizado com sucesso!')
            return redirect('dashboard:visualizar', pk=pk)
    else:
        cliente_form = DadosPessoaisForm(instance=curriculo.cliente)
        escolaridade_form = EscolaridadeForm(instance=curriculo)
        extras_form = InformacoesExtrasForm(instance=curriculo)

    return render(request, 'dashboard/editar.html', {
        'curriculo': curriculo,
        'cliente': curriculo.cliente,
        'cliente_form': cliente_form,
        'escolaridade_form': escolaridade_form,
        'extras_form': extras_form,
        'experiencias': curriculo.experiencias.all(),
        'cursos': curriculo.cursos.all(),
        'experiencia_form': ExperienciaForm(),
        'curso_form': CursoForm(),
    })


@login_required(login_url='accounts:login')
@user_passes_test(pode_acessar_painel, login_url='accounts:login')
def alterar_status(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False})

    curriculo = _get_curriculo_ou_404(request, pk)
    novo_status = request.POST.get('status')

    from curriculos.models import Curriculo
    if novo_status not in dict(Curriculo.STATUS_CHOICES):
        return JsonResponse({'success': False, 'error': 'Status inválido'})

    notificacao = None
    if novo_status == 'pago' and curriculo.status in ('pendente', 'cancelado'):
        curriculo.marcar_como_pago()
        try:
            notificacao = processar_pagamento_confirmado(curriculo)
        except Exception as exc:
            return JsonResponse({
                'success': False,
                'error': f'Pagamento marcado, mas falhou ao gerar PDF: {exc}',
                'status': curriculo.status,
                'status_display': curriculo.get_status_display(),
            })
    elif novo_status == 'pago' and curriculo.status in ('pago', 'enviado'):
        try:
            _garantir_pdf(curriculo)
        except Exception as exc:
            return JsonResponse({'success': False, 'error': f'Erro ao gerar PDF: {exc}'})
    else:
        curriculo.status = novo_status
        curriculo.save()

    response = {
        'success': True,
        'status': curriculo.status,
        'status_display': curriculo.get_status_display(),
    }
    if notificacao:
        response['whatsapp_link'] = notificacao['link']
        response['mensagem'] = (
            'PDF gerado! Baixe o arquivo e anexe no WhatsApp do cliente.'
        )

    return JsonResponse(response)


@login_required(login_url='accounts:login')
@user_passes_test(pode_acessar_painel, login_url='accounts:login')
def excluir_curriculo(request, pk):
    if not pode_excluir_curriculo(request.user):
        messages.error(request, 'Você não tem permissão para excluir currículos.')
        return redirect('dashboard:lista')

    curriculo = _get_curriculo_ou_404(request, pk)
    if request.method == 'POST':
        nome = curriculo.cliente.nome_completo
        curriculo.cliente.delete()
        messages.success(request, f'Currículo de {nome} excluído.')
        return redirect('dashboard:lista')
    return render(request, 'dashboard/confirmar_exclusao.html', {'curriculo': curriculo})


@login_required(login_url='accounts:login')
@user_passes_test(pode_acessar_painel, login_url='accounts:login')
def baixar_pdf(request, pk):
    curriculo = _get_curriculo_ou_404(request, pk)

    if not curriculo_pode_ter_pdf(curriculo):
        messages.error(request, 'O PDF só fica disponível após marcar o currículo como Pago.')
        return redirect('dashboard:visualizar', pk=pk)

    try:
        curriculo = _garantir_pdf(curriculo)
    except Exception as exc:
        messages.error(request, f'Não foi possível gerar o PDF: {exc}')
        return redirect('dashboard:visualizar', pk=pk)

    safe_name = ''.join(
        c if c.isalnum() or c in (' ', '_', '-') else ''
        for c in (curriculo.cliente.nome_completo or 'curriculo')
    ).strip().replace(' ', '_') or 'curriculo'

    # Abre pelo caminho absoluto — mais estável no Windows/OneDrive
    try:
        filepath = curriculo.pdf_arquivo.path
    except Exception:
        filepath = None

    if not filepath or not os.path.isfile(filepath):
        messages.error(request, 'Arquivo PDF não encontrado no servidor. Tente Regenerar PDF.')
        return redirect('dashboard:visualizar', pk=pk)

    return FileResponse(
        open(filepath, 'rb'),
        as_attachment=True,
        filename=f'curriculo_{safe_name}.pdf',
        content_type='application/pdf',
    )


@login_required(login_url='accounts:login')
@user_passes_test(pode_acessar_painel, login_url='accounts:login')
def regenerar_pdf(request, pk):
    curriculo = _get_curriculo_ou_404(request, pk)

    if not curriculo_pode_ter_pdf(curriculo):
        messages.error(request, 'O PDF só pode ser gerado após marcar o currículo como Pago.')
        return redirect('dashboard:visualizar', pk=pk)

    try:
        curriculo = (
            type(curriculo).objects.select_related('cliente')
            .prefetch_related('experiencias', 'cursos')
            .get(pk=curriculo.pk)
        )
        pdf_path = gerar_pdf_curriculo(curriculo)
        curriculo.pdf_arquivo = pdf_path
        curriculo.save(update_fields=['pdf_arquivo'])
        messages.success(request, 'PDF regenerado com sucesso!')
    except Exception as exc:
        messages.error(request, f'Erro ao regenerar PDF: {exc}')
    return redirect('dashboard:visualizar', pk=pk)


@login_required(login_url='accounts:login')
@user_passes_test(pode_acessar_painel, login_url='accounts:login')
def reenviar_pdf(request, pk):
    curriculo = _get_curriculo_ou_404(request, pk)
    curriculo = type(curriculo).objects.select_related('cliente').get(pk=curriculo.pk)

    if not curriculo_pode_ter_pdf(curriculo):
        messages.error(request, 'Só é possível reenviar PDF de currículos pagos.')
        return redirect('dashboard:visualizar', pk=pk)

    try:
        curriculo = _garantir_pdf(curriculo)
    except Exception as exc:
        messages.error(request, f'PDF não encontrado e falhou ao gerar: {exc}')
        return redirect('dashboard:visualizar', pk=pk)

    from notifications.whatsapp import notificar_pagamento_confirmado
    notificacao = notificar_pagamento_confirmado(curriculo)
    return redirect(notificacao['link'])
