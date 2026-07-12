"""Views do fluxo de criação de currículo."""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.conf import settings

from clientes.models import Cliente
from .models import Curriculo, ExperienciaProfissional, Curso
from .forms import (
    DadosPessoaisForm, EscolaridadeForm, ExperienciaForm,
    CursoForm, InformacoesExtrasForm,
)


ETAPAS = {
    1: ('Dados Pessoais', DadosPessoaisForm),
    2: ('Escolaridade', EscolaridadeForm),
    3: ('Experiências', None),
    4: ('Cursos', None),
    5: ('Informações Extras', InformacoesExtrasForm),
}

CAMPOS_ETAPA_1 = [
    'nome_completo', 'email', 'telefone', 'estado_civil',
    'cidade', 'bairro', 'ano_nascimento',
]
CAMPOS_ETAPA_2 = [
    'escolaridade', 'instituicao_escolaridade',
    'curso_escolaridade', 'ano_conclusao_escolaridade',
]
CAMPOS_ETAPA_5 = [
    'tema', 'cnh', 'veiculo_proprio',
    'objetivo_profissional', 'sobre_mim', 'habilidades',
]


def _is_rascunho(data):
    return data.get('rascunho') in ('1', 'true', 'True', True)


def _salvar_rascunho_cliente(cliente, data):
    """Salva dados parciais do cliente sem validação completa."""
    for campo in CAMPOS_ETAPA_1:
        if campo not in data:
            continue
        valor = data.get(campo)
        if campo == 'ano_nascimento':
            if valor in (None, ''):
                continue
            try:
                cliente.ano_nascimento = int(valor)
            except (TypeError, ValueError):
                continue
        else:
            cliente.__setattr__(campo, valor or '')
    cliente.save()


def _salvar_rascunho_escolaridade(curriculo, data):
    """Salva escolaridade parcial sem validação completa."""
    for campo in CAMPOS_ETAPA_2:
        if campo not in data:
            continue
        valor = data.get(campo)
        if campo == 'ano_conclusao_escolaridade':
            if valor in (None, ''):
                curriculo.ano_conclusao_escolaridade = None
            else:
                try:
                    curriculo.ano_conclusao_escolaridade = int(valor)
                except (TypeError, ValueError):
                    pass
        else:
            curriculo.__setattr__(campo, valor or '')
    curriculo.save()


def _salvar_rascunho_extras(curriculo, data):
    """Salva informações extras parciais."""
    if 'tema' in data and data.get('tema') in dict(Curriculo.TEMA_CHOICES):
        curriculo.tema = data.get('tema')
    if 'cnh' in data:
        curriculo.cnh = data.get('cnh') or 'nao_possui'
    if 'veiculo_proprio' in data:
        curriculo.veiculo_proprio = data.get('veiculo_proprio') in ('1', 'true', 'True', True)
    if 'objetivo_profissional' in data:
        curriculo.objetivo_profissional = data.get('objetivo_profissional') or ''
    if 'sobre_mim' in data:
        curriculo.sobre_mim = data.get('sobre_mim') or ''
    if 'habilidades' in data:
        curriculo.habilidades = data.get('habilidades') or ''
    curriculo.save()


def _get_vendedor_da_sessao(request):
    """Retorna o vendedor ativo vinculado à sessão, se houver."""
    from accounts.models import Vendedor
    vendedor_id = request.session.get('vendedor_id')
    if not vendedor_id:
        return None
    try:
        return Vendedor.objects.get(pk=vendedor_id, ativo=True)
    except Vendedor.DoesNotExist:
        request.session.pop('vendedor_id', None)
        return None


def _aplicar_vendedor_no_curriculo(curriculo, vendedor):
    """Garante que o currículo aponte para o vendedor do link atual."""
    if not vendedor:
        return curriculo
    if curriculo.vendedor_id != vendedor.pk:
        curriculo.vendedor = vendedor
        curriculo.save(update_fields=['vendedor'])
    return curriculo


def _vincular_vendedor_sessao(request, vendedor):
    """Define o vendedor da sessão e sincroniza o currículo ativo."""
    request.session['vendedor_id'] = vendedor.pk
    request.session.modified = True

    curriculo_id = request.session.get('curriculo_id')
    if curriculo_id:
        curriculo = Curriculo.objects.filter(pk=curriculo_id).first()
        if curriculo:
            _aplicar_vendedor_no_curriculo(curriculo, vendedor)


def _get_or_create_curriculo(request):
    """Obtém ou cria currículo vinculado à sessão e ao vendedor."""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    vendedor = _get_vendedor_da_sessao(request)
    curriculo_id = request.session.get('curriculo_id')
    if curriculo_id:
        try:
            qs = Curriculo.objects.select_related('cliente', 'vendedor')
            curriculo = qs.get(pk=curriculo_id, session_key=session_key)
            return _aplicar_vendedor_no_curriculo(curriculo, vendedor)
        except Curriculo.DoesNotExist:
            pass

    cliente = Cliente.objects.create(
        nome_completo='', email='', telefone='', cidade=''
    )
    curriculo = Curriculo.objects.create(
        cliente=cliente,
        session_key=session_key,
        vendedor=vendedor,
    )
    request.session['curriculo_id'] = curriculo.pk
    return curriculo


def entrar_pagina_vendedor(request, slug):
    """Landing pública do vendedor (/p/<slug>/)."""
    from accounts.models import Vendedor
    from core.views import landing_context

    vendedor = get_object_or_404(Vendedor, slug=slug, ativo=True)
    _vincular_vendedor_sessao(request, vendedor)
    context = landing_context()
    context['vendedor'] = vendedor
    context['WHATSAPP_NUMBER'] = vendedor.whatsapp_link_number
    context['WHATSAPP_DISPLAY'] = vendedor.whatsapp_display
    return render(request, 'core/home.html', context)


def criar_curriculo(request):
    """Inicia o formulário multi-etapas."""
    curriculo = _get_or_create_curriculo(request)

    tema = request.GET.get('tema')
    if tema in dict(Curriculo.TEMA_CHOICES) and curriculo.tema != tema:
        curriculo.tema = tema
        curriculo.save(update_fields=['tema'])

    etapa = int(request.GET.get('etapa', curriculo.etapa_atual or 1))
    etapa = max(1, min(etapa, 5))
    vendedor = curriculo.vendedor or _get_vendedor_da_sessao(request)

    context = {
        'curriculo': curriculo,
        'cliente': curriculo.cliente,
        'etapa': etapa,
        'total_etapas': 5,
        'etapas_info': ETAPAS,
        'progresso': int((etapa / 5) * 100),
        'vendedor': vendedor,
        'temas': Curriculo.TEMA_CHOICES,
        'tema_cores': Curriculo.TEMA_CORES,
    }

    if etapa == 1:
        context['form'] = DadosPessoaisForm(instance=curriculo.cliente)
    elif etapa == 2:
        context['form'] = EscolaridadeForm(instance=curriculo)
    elif etapa == 3:
        context['experiencias'] = curriculo.experiencias.all()
        context['form'] = ExperienciaForm()
    elif etapa == 4:
        context['cursos'] = curriculo.cursos.all()
        context['form'] = CursoForm()
    elif etapa == 5:
        context['form'] = InformacoesExtrasForm(instance=curriculo)

    return render(request, 'curriculos/criar.html', context)


@require_POST
def salvar_etapa(request):
    """Auto-save via AJAX para cada etapa."""
    curriculo = _get_or_create_curriculo(request)
    content_type = (request.content_type or '').split(';')[0].strip()
    if content_type == 'application/json':
        data = json.loads(request.body)
        etapa = int(data.get('etapa', 1))
    else:
        data = request.POST
        etapa = int(request.POST.get('etapa', 1))
    rascunho = _is_rascunho(data)

    try:
        if etapa == 1:
            files = request.FILES or None
            if rascunho:
                _salvar_rascunho_cliente(curriculo.cliente, data)
                if files and files.get('foto'):
                    curriculo.cliente.foto = files['foto']
                    curriculo.cliente.save(update_fields=['foto'])
                return JsonResponse({'success': True, 'draft': True})

            form = DadosPessoaisForm(data, files, instance=curriculo.cliente)
            if form.is_valid():
                form.save()
                curriculo.etapa_atual = max(curriculo.etapa_atual, 1)
                curriculo.save(update_fields=['etapa_atual'])
                return JsonResponse({'success': True, 'message': 'Dados salvos!'})
            return JsonResponse({'success': False, 'errors': form.errors})

        elif etapa == 2:
            if rascunho:
                _salvar_rascunho_escolaridade(curriculo, data)
                return JsonResponse({'success': True, 'draft': True})

            form = EscolaridadeForm(data, instance=curriculo)
            if form.is_valid():
                form.save()
                curriculo.etapa_atual = max(curriculo.etapa_atual, 2)
                curriculo.save(update_fields=['etapa_atual'])
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'errors': form.errors})

        elif etapa == 3:
            sem_exp = data.get('sem_experiencia') in ('true', 'True', True, 'on')
            curriculo.sem_experiencia = sem_exp
            if not rascunho:
                curriculo.etapa_atual = max(curriculo.etapa_atual, 3)
            curriculo.save()
            return JsonResponse({'success': True, 'draft': rascunho})

        elif etapa == 4:
            sem_cur = data.get('sem_cursos') in ('true', 'True', True, 'on')
            curriculo.sem_cursos = sem_cur
            if not rascunho:
                curriculo.etapa_atual = max(curriculo.etapa_atual, 4)
            curriculo.save()
            return JsonResponse({'success': True, 'draft': rascunho})

        elif etapa == 5:
            if rascunho:
                _salvar_rascunho_extras(curriculo, data)
                return JsonResponse({'success': True, 'draft': True})

            form = InformacoesExtrasForm(data, instance=curriculo)
            if form.is_valid():
                form.save()
                curriculo.etapa_atual = 5
                curriculo.save()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'errors': form.errors})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False})


@require_POST
def adicionar_experiencia(request):
    """Adiciona experiência profissional via AJAX."""
    curriculo = _get_or_create_curriculo(request)
    data = json.loads(request.body)
    form = ExperienciaForm(data)
    if form.is_valid():
        exp = form.save(commit=False)
        exp.curriculo = curriculo
        exp.ordem = curriculo.experiencias.count()
        exp.save()
        return JsonResponse({
            'success': True,
            'experiencia': {
                'id': exp.pk,
                'empresa': exp.empresa,
                'cargo': exp.cargo,
                'periodo': exp.periodo,
                'descricao': exp.descricao,
            },
        })
    return JsonResponse({'success': False, 'errors': form.errors})


@require_POST
def remover_experiencia(request, pk):
    """Remove experiência profissional."""
    curriculo = _get_or_create_curriculo(request)
    ExperienciaProfissional.objects.filter(pk=pk, curriculo=curriculo).delete()
    return JsonResponse({'success': True})


@require_POST
def adicionar_curso(request):
    """Adiciona curso via AJAX."""
    curriculo = _get_or_create_curriculo(request)
    data = json.loads(request.body)
    form = CursoForm(data)
    if form.is_valid():
        curso = form.save(commit=False)
        curso.curriculo = curriculo
        curso.ordem = curriculo.cursos.count()
        curso.save()
        return JsonResponse({
            'success': True,
            'curso': {
                'id': curso.pk,
                'nome': curso.nome,
                'instituicao': curso.instituicao,
                'carga_horaria': curso.carga_horaria,
                'ano': curso.ano,
            },
        })
    return JsonResponse({'success': False, 'errors': form.errors})


@require_POST
def remover_curso(request, pk):
    """Remove curso."""
    curriculo = _get_or_create_curriculo(request)
    Curso.objects.filter(pk=pk, curriculo=curriculo).delete()
    return JsonResponse({'success': True})


def finalizar_curriculo(request):
    """Finaliza criação e exibe prévia protegida."""
    curriculo = _get_or_create_curriculo(request)
    vendedor = _get_vendedor_da_sessao(request)
    if vendedor:
        _aplicar_vendedor_no_curriculo(curriculo, vendedor)

    if not curriculo.cliente.nome_completo:
        messages.error(request, 'Preencha seus dados pessoais antes de finalizar.')
        return redirect('curriculos:criar')

    curriculo.etapa_atual = 5
    curriculo.save()

    return render(request, 'curriculos/finalizado.html', {
        'curriculo': curriculo,
        'cliente': curriculo.cliente,
        'vendedor': curriculo.vendedor or vendedor,
    })


def preview_curriculo(request, pk):
    """Prévia protegida do currículo."""
    curriculo = get_object_or_404(
        Curriculo.objects.select_related('cliente').prefetch_related(
            'experiencias', 'cursos'
        ),
        pk=pk,
    )
    return render(request, 'curriculos/preview.html', {
        'curriculo': curriculo,
        'cliente': curriculo.cliente,
        'protegido': True,
    })


def whatsapp_adquirir(request, pk):
    """Redireciona para WhatsApp do vendedor do link (/p/slug/), não o global."""
    from notifications.whatsapp import gerar_link_whatsapp, obter_mensagem

    curriculo = get_object_or_404(
        Curriculo.objects.select_related('cliente', 'vendedor'),
        pk=pk,
    )

    # Prioridade: vendedor da sessão (link /p/...) > vendedor já salvo no currículo
    vendedor = _get_vendedor_da_sessao(request)
    if vendedor:
        _aplicar_vendedor_no_curriculo(curriculo, vendedor)
    elif curriculo.vendedor_id:
        vendedor = curriculo.vendedor
        request.session['vendedor_id'] = vendedor.pk
        request.session.modified = True

    nome = curriculo.cliente.nome_completo or 'cliente'
    mensagem = obter_mensagem('adquirir', nome=nome)
    if vendedor and vendedor.whatsapp:
        numero = vendedor.whatsapp_link_number
    else:
        numero = settings.WHATSAPP_NUMBER
    return redirect(gerar_link_whatsapp(numero, mensagem))
