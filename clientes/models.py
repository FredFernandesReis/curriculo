"""
Modelos relacionados aos clientes do sistema.
"""
from django.db import models


class Cliente(models.Model):
    """Dados pessoais do cliente que solicita o currículo."""

    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)'),
        ('uniao_estavel', 'União Estável'),
    ]

    nome_completo = models.CharField('Nome completo', max_length=200)
    email = models.EmailField('E-mail')
    telefone = models.CharField('Telefone', max_length=20)
    estado_civil = models.CharField(
        'Estado civil', max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True
    )
    cidade = models.CharField('Cidade', max_length=100)
    bairro = models.CharField('Bairro', max_length=100, blank=True)
    ano_nascimento = models.PositiveIntegerField('Ano de nascimento', null=True, blank=True)
    foto = models.ImageField(
        'Foto',
        upload_to='clientes/fotos/',
        blank=True,
        null=True,
        help_text='Foto 3x4 ou retrato (opcional)',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome_completo

    @property
    def telefone_whatsapp(self):
        """Retorna telefone formatado para link do WhatsApp."""
        numeros = ''.join(filter(str.isdigit, self.telefone))
        if not numeros.startswith('55'):
            numeros = '55' + numeros
        return numeros
