"""Gerador de PDF com topo colorido e foto arredondada."""
import io
import os
import tempfile
from datetime import date
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, HRFlowable, Spacer,
    Table, TableStyle, Image, KeepInFrame, Flowable,
)
from django.conf import settings


TEMA_CORES = {
    'azul': {'primary': colors.HexColor('#1e3a5f'), 'accent': colors.HexColor('#1e4e8c')},
    'verde': {'primary': colors.HexColor('#14532d'), 'accent': colors.HexColor('#15803d')},
    'roxo': {'primary': colors.HexColor('#4c1d95'), 'accent': colors.HexColor('#6d28d9')},
}


class BannerFundo(Flowable):
    """Faixa colorida de fundo atrás do cabeçalho."""

    def __init__(self, width, height, cor):
        super().__init__()
        self.width = width
        self.height = height
        self.cor = cor

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        self.canv.setFillColor(self.cor)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)


def _idade(ano_nascimento):
    if not ano_nascimento:
        return None
    hoje = date.today()
    return max(0, hoje.year - int(ano_nascimento))


def _texto_pdf(valor):
    if valor is None:
        return ''
    texto = str(valor).replace('\r\n', '\n').replace('\r', '\n')
    return escape(texto).replace('\n', '<br/>')


def _p(texto, style):
    return Paragraph(_texto_pdf(texto), style)


def _bullets_da_descricao(texto):
    if not texto:
        return []
    texto = texto.replace('\r\n', '\n').replace('\r', '\n')
    partes = []
    for bloco in texto.split('\n'):
        bloco = bloco.strip(' •-\t')
        if not bloco:
            continue
        if ';' in bloco and len(bloco) > 40:
            for p in bloco.split(';'):
                p = p.strip(' •-\t')
                if p:
                    partes.append(p)
        else:
            partes.append(bloco)
    return partes


def _foto_arredondada(foto_path, diametro_px=280):
    """Gera PNG circular temporário da foto."""
    try:
        from PIL import Image as PILImage, ImageDraw
    except ImportError:
        return None

    try:
        im = PILImage.open(foto_path).convert('RGBA')
    except OSError:
        return None

    size = (diametro_px, diametro_px)
    # Crop central quadrado
    w, h = im.size
    lado = min(w, h)
    left = (w - lado) // 2
    top = (h - lado) // 2
    im = im.crop((left, top, left + lado, top + lado)).resize(size, PILImage.LANCZOS)

    mask = PILImage.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, diametro_px - 1, diametro_px - 1), fill=255)

    output = PILImage.new('RGBA', size, (0, 0, 0, 0))
    output.paste(im, (0, 0))
    output.putalpha(mask)

    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    output.save(tmp.name, format='PNG')
    tmp.close()
    return tmp.name


def _criar_estilos(accent, nome_branco=False):
    styles = getSampleStyleSheet()
    cor_nome = colors.white if nome_branco else colors.HexColor('#111111')
    cor_dado = colors.Color(1, 1, 1, alpha=0.92) if nome_branco else colors.HexColor('#444444')

    styles.add(ParagraphStyle(
        name='CvNome',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=cor_nome,
        spaceAfter=4,
        leading=20,
    ))
    styles.add(ParagraphStyle(
        name='CvDado',
        fontName='Helvetica',
        fontSize=9.5,
        textColor=cor_dado,
        spaceAfter=2,
        leading=13,
    ))
    styles.add(ParagraphStyle(
        name='CvSecao',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=accent,
        spaceBefore=12,
        spaceAfter=3,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name='CvCargo',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#222222'),
        spaceBefore=8,
        spaceAfter=3,
        leading=13,
    ))
    styles.add(ParagraphStyle(
        name='CvCorpo',
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#444444'),
        alignment=TA_JUSTIFY,
        spaceAfter=4,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name='CvBullet',
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#444444'),
        leading=13,
        leftIndent=8,
        spaceAfter=3,
    ))
    return styles


def _titulo_secao(texto, styles, accent):
    return [
        Paragraph(texto.upper(), styles['CvSecao']),
        HRFlowable(
            width='100%', thickness=1.2, color=accent,
            spaceBefore=0, spaceAfter=6,
        ),
    ]


def _lista_bullets(itens, styles):
    if not itens:
        return []
    return [_p(f'•  {item}', styles['CvBullet']) for item in itens]


def gerar_pdf_curriculo(curriculo):
    """Gera PDF com topo colorido e foto circular."""
    cliente = curriculo.cliente
    tema = getattr(curriculo, 'tema', None) or 'azul'
    cores = TEMA_CORES.get(tema, TEMA_CORES['azul'])
    primary = cores['primary']
    accent = cores['accent']

    buffer = io.BytesIO()
    page_w, page_h = A4
    left = 1.6 * cm
    right = 1.6 * cm
    usable = page_w - left - right

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=right,
        leftMargin=left,
        topMargin=1.2 * cm,
        bottomMargin=1.4 * cm,
    )

    styles_banner = _criar_estilos(accent, nome_branco=True)
    styles = _criar_estilos(accent, nome_branco=False)
    el = []
    tmp_foto = None

    # --- Cabeçalho colorido ---
    dados_header = []
    dados_header.append(_p(cliente.nome_completo or 'Currículo', styles_banner['CvNome']))

    linha_pessoal = []
    if cliente.estado_civil:
        civil = dict(cliente.ESTADO_CIVIL_CHOICES).get(
            cliente.estado_civil, cliente.estado_civil
        )
        linha_pessoal.append(civil)
    idade = _idade(cliente.ano_nascimento)
    if idade:
        linha_pessoal.append(f'{idade} anos')
    if linha_pessoal:
        dados_header.append(_p(', '.join(linha_pessoal), styles_banner['CvDado']))

    if cliente.cidade or cliente.bairro:
        endereco = []
        if cliente.bairro:
            endereco.append(cliente.bairro)
        if cliente.cidade:
            endereco.append(cliente.cidade)
        dados_header.append(_p(' – '.join(endereco), styles_banner['CvDado']))

    if cliente.telefone:
        dados_header.append(_p(f'Telefone: {cliente.telefone}', styles_banner['CvDado']))
    if cliente.email:
        dados_header.append(_p(f'E-mail: {cliente.email}', styles_banner['CvDado']))
    if curriculo.cnh and curriculo.cnh != 'nao_possui':
        cnh = dict(curriculo.CNH_CHOICES).get(curriculo.cnh, curriculo.cnh)
        dados_header.append(_p(f'CNH: {cnh}', styles_banner['CvDado']))
    if curriculo.veiculo_proprio:
        dados_header.append(_p('Veículo próprio: Sim', styles_banner['CvDado']))

    foto_flowable = None
    if cliente.foto:
        try:
            foto_path = cliente.foto.path
            if os.path.isfile(foto_path):
                tmp_foto = _foto_arredondada(foto_path)
                src = tmp_foto or foto_path
                foto_flowable = Image(src, width=2.3 * cm, height=2.3 * cm)
                foto_flowable.hAlign = 'RIGHT'
        except (ValueError, OSError):
            foto_flowable = None

    esquerda = KeepInFrame(
        usable - 3.2 * cm,
        3.4 * cm,
        dados_header,
        mode='shrink',
        hAlign='LEFT',
        vAlign='MIDDLE',
    )

    if foto_flowable:
        header_inner = Table(
            [[esquerda, foto_flowable]],
            colWidths=[usable - 3.2 * cm, 3.0 * cm],
        )
    else:
        header_inner = Table([[esquerda]], colWidths=[usable])

    header_inner.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (-1, -1), primary),
    ]))
    el.append(header_inner)
    el.append(Spacer(1, 10))

    # Objetivo
    if curriculo.objetivo_profissional:
        el.extend(_titulo_secao('Objetivo Profissional', styles, accent))
        el.append(_p(curriculo.objetivo_profissional, styles['CvCorpo']))

    # Sobre mim
    sobre = getattr(curriculo, 'sobre_mim', '') or ''
    if sobre:
        el.extend(_titulo_secao('Sobre Mim', styles, accent))
        el.append(_p(sobre, styles['CvCorpo']))

    # Formação
    if curriculo.escolaridade:
        el.extend(_titulo_secao('Formação Acadêmica', styles, accent))
        esc = dict(curriculo.ESCOLARIDADE_CHOICES).get(
            curriculo.escolaridade, curriculo.escolaridade
        )
        titulo = esc
        if curriculo.curso_escolaridade:
            titulo = f'{curriculo.curso_escolaridade}'
            if curriculo.ano_conclusao_escolaridade:
                titulo += f' – Conclusão em {curriculo.ano_conclusao_escolaridade}'
        elif curriculo.ano_conclusao_escolaridade:
            titulo += f' – Conclusão em {curriculo.ano_conclusao_escolaridade}'
        el.append(_p(titulo, styles['CvCorpo']))
        if curriculo.instituicao_escolaridade:
            el.append(_p(curriculo.instituicao_escolaridade, styles['CvCorpo']))
        if curriculo.curso_escolaridade and curriculo.escolaridade:
            el.append(_p(f'Nível: {esc}', styles['CvCorpo']))

    # Experiências
    experiencias = list(curriculo.experiencias.all())
    if experiencias or curriculo.sem_experiencia:
        el.extend(_titulo_secao('Experiência Profissional', styles, accent))
        if curriculo.sem_experiencia and not experiencias:
            el.append(_p(
                'Busca primeira oportunidade no mercado de trabalho.',
                styles['CvCorpo'],
            ))
        for exp in experiencias:
            cab = f'{exp.empresa} – {exp.cargo}'
            if exp.periodo:
                cab += f' | {exp.periodo}'
            el.append(_p(cab, styles['CvCargo']))
            bullets = _bullets_da_descricao(exp.descricao)
            if bullets:
                el.extend(_lista_bullets(bullets, styles))
            elif exp.descricao:
                el.append(_p(exp.descricao, styles['CvCorpo']))

    # Habilidades
    habilidades = _bullets_da_descricao(getattr(curriculo, 'habilidades', '') or '')
    if habilidades:
        el.extend(_titulo_secao('Habilidades', styles, accent))
        el.extend(_lista_bullets(habilidades, styles))

    # Cursos
    cursos = list(curriculo.cursos.all())
    if cursos and not curriculo.sem_cursos:
        el.extend(_titulo_secao('Cursos e Capacitações', styles, accent))
        itens = []
        for curso in cursos:
            linha = curso.nome
            extras = []
            if curso.instituicao:
                extras.append(curso.instituicao)
            if curso.carga_horaria:
                extras.append(curso.carga_horaria)
            if curso.ano:
                extras.append(str(curso.ano))
            if extras:
                linha += f' – {" · ".join(extras)}'
            itens.append(linha)
        el.extend(_lista_bullets(itens, styles))

    try:
        doc.build(el)
    finally:
        if tmp_foto and os.path.isfile(tmp_foto):
            try:
                os.unlink(tmp_foto)
            except OSError:
                pass

    buffer.seek(0)
    safe_name = ''.join(
        c if c.isalnum() or c in (' ', '_', '-') else ''
        for c in (cliente.nome_completo or 'curriculo')
    ).strip().replace(' ', '_') or 'curriculo'
    filename = f'curriculo_{safe_name}_{curriculo.pk}.pdf'
    filepath = os.path.join(settings.MEDIA_ROOT, 'curriculos', 'pdf', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())

    return f'curriculos/pdf/{filename}'
