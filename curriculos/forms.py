"""Formulários do fluxo de criação de currículo."""
from django import forms
from clientes.models import Cliente
from curriculos.models import Curriculo, ExperienciaProfissional, Curso


class DadosPessoaisForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nome_completo', 'email', 'telefone', 'estado_civil',
            'cidade', 'bairro', 'ano_nascimento', 'foto',
        ]
        widgets = {
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Seu nome completo',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'seu@email.com',
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '(31) 99999-9999',
                'data-mask': 'phone',
            }),
            'estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Sua cidade',
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Seu bairro',
            }),
            'ano_nascimento': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': '1990',
                'min': '1940', 'max': '2010',
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control form-control-sm',
                'accept': 'image/*',
                'id': 'id_foto',
            }),
        }


class EscolaridadeForm(forms.ModelForm):
    class Meta:
        model = Curriculo
        fields = [
            'escolaridade', 'instituicao_escolaridade',
            'curso_escolaridade', 'ano_conclusao_escolaridade',
        ]
        widgets = {
            'escolaridade': forms.Select(attrs={'class': 'form-select'}),
            'instituicao_escolaridade': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nome da instituição',
            }),
            'curso_escolaridade': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nome do curso',
            }),
            'ano_conclusao_escolaridade': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': '2020',
                'min': '1950', 'max': '2030',
            }),
        }


class ExperienciaForm(forms.ModelForm):
    class Meta:
        model = ExperienciaProfissional
        fields = ['empresa', 'cargo', 'periodo', 'descricao']
        widgets = {
            'empresa': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nome da empresa',
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Seu cargo',
            }),
            'periodo': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Jan/2020 - Dez/2023',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Uma atividade por linha (vira tópico no currículo)...',
            }),
        }


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nome', 'instituicao', 'carga_horaria', 'ano']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nome do curso *',
            }),
            'instituicao': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Instituição (opcional)',
            }),
            'carga_horaria': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '40 horas',
            }),
            'ano': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': '2023',
                'min': '1950', 'max': '2030',
            }),
        }


class InformacoesExtrasForm(forms.ModelForm):
    veiculo_proprio = forms.TypedChoiceField(
        choices=[('1', 'Sim'), ('0', 'Não')],
        coerce=lambda x: x == '1',
        widget=forms.RadioSelect,
        required=False,
        label='Veículo próprio',
    )

    class Meta:
        model = Curriculo
        fields = [
            'tema', 'cnh', 'veiculo_proprio',
            'objetivo_profissional', 'sobre_mim', 'habilidades',
        ]
        labels = {
            'tema': 'Cor do currículo',
            'objetivo_profissional': 'Objetivo profissional',
            'sobre_mim': 'Sobre mim',
            'habilidades': 'Habilidades',
        }
        widgets = {
            'tema': forms.Select(attrs={'class': 'form-select'}),
            'cnh': forms.Select(attrs={'class': 'form-select'}),
            'objetivo_profissional': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': (
                    'Ex: Busco oportunidade na área administrativa, '
                    'com foco em organização e atendimento ao cliente.'
                ),
            }),
            'sobre_mim': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': (
                    'Fale um pouco sobre você: quem é, pontos fortes '
                    'e o que oferece às empresas...'
                ),
            }),
            'habilidades': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Uma habilidade por linha\nEx:\nComunicação\nTrabalho em equipe\nPacote Office',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['veiculo_proprio'].initial = '1' if self.instance.veiculo_proprio else '0'
