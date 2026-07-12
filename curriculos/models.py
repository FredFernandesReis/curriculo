"""
Modelos do currículo e suas seções.
"""
from django.db import models
from django.utils import timezone
from clientes.models import Cliente


class Curriculo(models.Model):
    """Currículo principal com status e controle de pagamento."""

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('enviado', 'Enviado'),
        ('cancelado', 'Cancelado'),
    ]

    CNH_CHOICES = [
        ('nao_possui', 'Não possui'),
        ('A', 'Categoria A'),
        ('B', 'Categoria B'),
        ('AB', 'Categoria AB'),
        ('C', 'Categoria C'),
        ('D', 'Categoria D'),
        ('E', 'Categoria E'),
    ]

    ESCOLARIDADE_CHOICES = [
        ('fundamental', 'Ensino Fundamental'),
        ('medio', 'Ensino Médio'),
        ('tecnico', 'Curso Técnico'),
        ('faculdade', 'Faculdade'),
        ('pos_graduacao', 'Pós-graduação'),
    ]

    TEMA_CHOICES = [
        ('azul', 'Azul — Profissional'),
        ('verde', 'Verde — Moderno'),
        ('roxo', 'Roxo — Elegante'),
    ]

    TEMA_CORES = {
        'azul': {'primary': '#1e3a5f', 'accent': '#1e4e8c', 'light': '#eff6ff'},
        'verde': {'primary': '#14532d', 'accent': '#15803d', 'light': '#f0fdf4'},
        'roxo': {'primary': '#4c1d95', 'accent': '#6d28d9', 'light': '#f5f3ff'},
    }

    cliente = models.OneToOneField(
        Cliente, on_delete=models.CASCADE, related_name='curriculo'
    )
    vendedor = models.ForeignKey(
        'accounts.Vendedor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='curriculos',
        verbose_name='Vendedor',
    )
    status = models.CharField(
        'Status', max_length=20, choices=STATUS_CHOICES, default='pendente'
    )
    tema = models.CharField(
        'Cor do currículo',
        max_length=20,
        choices=TEMA_CHOICES,
        default='azul',
    )

    # Escolaridade
    escolaridade = models.CharField(
        'Escolaridade', max_length=20, choices=ESCOLARIDADE_CHOICES, blank=True
    )
    instituicao_escolaridade = models.CharField(
        'Instituição', max_length=200, blank=True
    )
    curso_escolaridade = models.CharField('Curso', max_length=200, blank=True)
    ano_conclusao_escolaridade = models.PositiveIntegerField(
        'Ano de conclusão', null=True, blank=True
    )

    # Informações extras
    cnh = models.CharField(
        'CNH', max_length=20, choices=CNH_CHOICES, default='nao_possui'
    )
    veiculo_proprio = models.BooleanField('Veículo próprio', default=False)
    objetivo_profissional = models.TextField(
        'Objetivo profissional',
        blank=True,
        help_text='Objetivo de carreira em poucas linhas.',
    )
    sobre_mim = models.TextField(
        'Sobre mim',
        blank=True,
        help_text='Texto livre para a pessoa se apresentar.',
    )
    habilidades = models.TextField(
        'Habilidades',
        blank=True,
        help_text='Uma habilidade por linha.',
    )

    # Flags
    sem_experiencia = models.BooleanField('Sem experiência profissional', default=False)
    sem_cursos = models.BooleanField('Sem cursos', default=False)

    # Controle
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    etapa_atual = models.PositiveSmallIntegerField('Etapa atual', default=1)
    pdf_arquivo = models.FileField('PDF', upload_to='curriculos/pdf/', blank=True)
    data_pagamento = models.DateTimeField('Data do pagamento', null=True, blank=True)
    data_envio = models.DateTimeField('Data de envio', null=True, blank=True)
    valor_pago = models.DecimalField(
        'Valor pago', max_digits=10, decimal_places=2, null=True, blank=True
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Currículo'
        verbose_name_plural = 'Currículos'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Currículo de {self.cliente.nome_completo}'

    def cores_tema(self):
        return self.TEMA_CORES.get(self.tema, self.TEMA_CORES['azul'])

    def marcar_como_pago(self, valor=None):
        """Marca currículo como pago e dispara geração de PDF."""
        from django.conf import settings
        self.status = 'pago'
        self.data_pagamento = timezone.now()
        self.valor_pago = valor or settings.CURRICULO_PRECO
        self.save()

    def marcar_como_enviado(self):
        """Marca currículo como enviado."""
        self.status = 'enviado'
        self.data_envio = timezone.now()
        self.save()


class ExperienciaProfissional(models.Model):
    """Experiência profissional do candidato."""

    curriculo = models.ForeignKey(
        Curriculo, on_delete=models.CASCADE, related_name='experiencias'
    )
    empresa = models.CharField('Empresa', max_length=200)
    cargo = models.CharField('Cargo', max_length=200)
    periodo = models.CharField('Período', max_length=100)
    descricao = models.TextField('Descrição das atividades', blank=True)
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Experiência Profissional'
        verbose_name_plural = 'Experiências Profissionais'
        ordering = ['ordem', '-id']

    def __str__(self):
        return f'{self.cargo} - {self.empresa}'


class Curso(models.Model):
    """Curso complementar do candidato."""

    curriculo = models.ForeignKey(
        Curriculo, on_delete=models.CASCADE, related_name='cursos'
    )
    nome = models.CharField('Nome do curso', max_length=200)
    instituicao = models.CharField('Instituição', max_length=200, blank=True)
    carga_horaria = models.CharField('Carga horária', max_length=50, blank=True)
    ano = models.PositiveIntegerField('Ano', null=True, blank=True)
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['ordem', '-id']

    def __str__(self):
        return self.nome
