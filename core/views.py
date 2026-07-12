"""Views da landing page e páginas públicas."""
from django.shortcuts import render


def landing_context():
    """Contexto compartilhado da landing."""
    return {
        'avaliacoes': [
            {
                'nome': 'Maria Silva',
                'cargo': 'Assistente Administrativa',
                'texto': 'Meu currículo ficou incrível! Consegui 3 entrevistas na primeira semana.',
                'estrelas': 5,
            },
            {
                'nome': 'João Santos',
                'cargo': 'Técnico em Informática',
                'texto': 'Profissionalismo total. O layout é moderno e chamou a atenção dos recrutadores.',
                'estrelas': 5,
            },
            {
                'nome': 'Ana Oliveira',
                'cargo': 'Auxiliar de Produção',
                'texto': 'Processo super fácil e rápido. Recomendo para quem precisa de um currículo de qualidade.',
                'estrelas': 5,
            },
            {
                'nome': 'Carlos Mendes',
                'cargo': 'Motorista',
                'texto': 'Excelente atendimento e currículo muito bem formatado. Vale cada centavo!',
                'estrelas': 5,
            },
        ],
        'faqs': [
            {
                'pergunta': 'Como funciona o processo?',
                'resposta': 'Você preenche seus dados em um formulário simples, visualiza uma prévia do currículo e, após o pagamento, recebe o PDF profissional pelo WhatsApp.',
            },
            {
                'pergunta': 'Quanto tempo leva para receber o currículo?',
                'resposta': 'Após a confirmação do pagamento, você recebe o PDF em até 24 horas, geralmente em poucas horas.',
            },
            {
                'pergunta': 'Posso editar meu currículo depois?',
                'resposta': 'Sim! Entre em contato conosco pelo WhatsApp e faremos as alterações necessárias.',
            },
            {
                'pergunta': 'Qual a forma de pagamento?',
                'resposta': 'Aceitamos PIX. Após criar seu currículo, você será direcionado ao WhatsApp para finalizar o pagamento.',
            },
            {
                'pergunta': 'O currículo é compatível com sistemas ATS?',
                'resposta': 'Sim! Nossos currículos são formatados de forma profissional e legível por sistemas de triagem automatizada.',
            },
        ],
    }


def home(request):
    """Landing page principal do sistema."""
    return render(request, 'core/home.html', landing_context())
