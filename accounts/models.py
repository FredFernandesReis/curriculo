"""Perfil de vendedor/parceiro do sistema."""
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Vendedor(models.Model):
    """Conta de parceiro: página pública e WhatsApp próprios."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendedor',
    )
    nome_publico = models.CharField('Nome público', max_length=120)
    slug = models.SlugField('Slug da página', max_length=80, unique=True)
    whatsapp = models.CharField(
        'WhatsApp',
        max_length=20,
        help_text='Somente números, com DDD. Ex: 31988702824',
    )
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'
        ordering = ['nome_publico']

    def __str__(self):
        return self.nome_publico

    def save(self, *args, **kwargs):
        if not self.slug and self.nome_publico:
            base = slugify(self.nome_publico)[:70] or 'parceiro'
            slug = base
            n = 1
            while Vendedor.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f'{base}-{n}'
            self.slug = slug
        self.whatsapp = ''.join(filter(str.isdigit, self.whatsapp or ''))
        super().save(*args, **kwargs)

    @property
    def whatsapp_link_number(self):
        """Número formatado para wa.me (com 55 se necessário)."""
        numeros = ''.join(filter(str.isdigit, self.whatsapp or ''))
        if not numeros.startswith('55'):
            numeros = '55' + numeros
        return numeros

    @property
    def whatsapp_display(self):
        n = ''.join(filter(str.isdigit, self.whatsapp or ''))
        if len(n) >= 11:
            return f'({n[-11:-9]}) {n[-9:-4]}-{n[-4:]}'
        return self.whatsapp

    def get_public_path(self):
        return f'/p/{self.slug}/'
