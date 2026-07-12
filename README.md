# Currículo PRO

Sistema SaaS de criação de currículos profissionais em Django.

## Requisitos

- Python 3.10+
- pip

## Instalação

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Acesso

- **Site:** http://127.0.0.1:8000/
- **Painel Admin:** http://127.0.0.1:8000/painel/
- **Django Admin:** http://127.0.0.1:8000/admin/

## Estrutura

| App | Função |
|-----|--------|
| `core` | Landing page |
| `accounts` | Autenticação |
| `clientes` | Dados pessoais |
| `curriculos` | Formulário e prévia |
| `dashboard` | Painel administrativo |
| `pdf_generator` | Geração de PDF |
| `notifications` | WhatsApp |

## Produção

Configure as variáveis de ambiente:

```
SECRET_KEY=sua-chave-secreta
DEBUG=False
ALLOWED_HOSTS=seudominio.com
DATABASE_URL=postgres://user:pass@host:5432/dbname
```

## Fluxo

1. Usuário preenche formulário em etapas
2. Visualiza prévia protegida com marca d'água
3. Solicita versão PDF via WhatsApp
4. Admin confirma pagamento no painel
5. Sistema gera PDF e prepara envio via WhatsApp
