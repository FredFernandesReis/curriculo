"""Formulários de autenticação do parceiro."""
from django import forms

from .models import Vendedor


class PerfilVendedorForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = ['nome_publico', 'whatsapp']
        widgets = {
            'nome_publico': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Currículos da Maria',
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '31988702824',
            }),
        }
