"""Admin para criar vendedores (parceiros)."""
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Vendedor

User = get_user_model()


class VendedorAdminForm(forms.ModelForm):
    username = forms.CharField(label='Usuário de login', max_length=150)
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput,
        required=False,
        help_text='Obrigatória ao criar. Deixe em branco para manter a senha atual.',
    )

    class Meta:
        model = Vendedor
        fields = ['nome_publico', 'slug', 'whatsapp', 'ativo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user_id:
            self.fields['username'].initial = self.instance.user.username
            self.fields['password'].help_text = 'Deixe em branco para não alterar a senha.'
        else:
            self.fields['password'].required = True

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk and self.instance.user_id:
            qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists():
            raise forms.ValidationError('Este nome de usuário já existe.')
        return username

    def save(self, commit=True):
        vendedor = super().save(commit=False)
        username = self.cleaned_data['username']
        password = self.cleaned_data.get('password')

        if vendedor.pk and vendedor.user_id:
            user = vendedor.user
            user.username = username
            if password:
                user.set_password(password)
            user.save()
        else:
            user = User.objects.create_user(username=username, password=password)
            user.is_staff = False
            user.is_superuser = False
            user.save()
            vendedor.user = user

        if commit:
            vendedor.save()
        return vendedor


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    form = VendedorAdminForm
    list_display = ['nome_publico', 'slug', 'whatsapp', 'ativo', 'user', 'criado_em']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome_publico', 'slug', 'whatsapp', 'user__username']
    prepopulated_fields = {'slug': ('nome_publico',)}

    def get_fields(self, request, obj=None):
        return ['username', 'password', 'nome_publico', 'slug', 'whatsapp', 'ativo']
