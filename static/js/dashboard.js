// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-alterar-status').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const id = this.dataset.id;
            const status = this.dataset.status;

            if (!confirm(`Alterar status para "${this.textContent.trim()}"?`)) return;

            const formData = new FormData();
            formData.append('status', status);

            const resp = await fetch(`/painel/curriculo/${id}/status/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: formData,
            });

            const result = await resp.json();
            if (result.success) {
                if (result.whatsapp_link) {
                    if (confirm(result.mensagem + '\n\nAbrir WhatsApp para enviar?')) {
                        window.open(result.whatsapp_link, '_blank');
                    }
                }
                location.reload();
            } else {
                alert('Erro ao alterar status: ' + (result.error || 'Erro desconhecido'));
            }
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
