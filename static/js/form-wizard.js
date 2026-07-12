// Form Wizard - Auto-save silencioso e validação apenas ao avançar
document.addEventListener('DOMContentLoaded', function() {
    const formEtapa = document.getElementById('form-etapa');
    const btnProximo = document.getElementById('btnProximo');
    const btnFinalizar = document.getElementById('btnFinalizar');

    // Auto-save silencioso ao digitar (sem alertas de erro)
    if (formEtapa) {
        let saveTimeout;
        formEtapa.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('input', () => {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => salvarRascunho(formEtapa), 1200);
            });
            field.addEventListener('change', () => salvarRascunho(formEtapa));
        });

        // Pré-visualização da foto 3x4
        const fotoInput = formEtapa.querySelector('input[name="foto"]');
        if (fotoInput) {
            fotoInput.addEventListener('change', function () {
                const file = this.files && this.files[0];
                const preview = document.getElementById('fotoPreview');
                const placeholder = document.getElementById('fotoPlaceholder');
                if (!file || !preview) return;
                const url = URL.createObjectURL(file);
                preview.src = url;
                preview.classList.remove('d-none');
                if (placeholder) placeholder.classList.add('d-none');
            });
        }
        // Destaca tema selecionado
        document.querySelectorAll('.tema-option input[name="tema"]').forEach(radio => {
            radio.addEventListener('change', () => {
                document.querySelectorAll('.tema-option').forEach(el => el.classList.remove('selected'));
                radio.closest('.tema-option')?.classList.add('selected');
                if (formEtapa) salvarRascunho(formEtapa);
            });
        });
    }

    // Botão próximo — valida só ao clicar
    if (btnProximo) {
        btnProximo.addEventListener('click', async function() {
            const etapa = parseInt(this.dataset.etapa);
            limparErrosFormulario();

            if (formEtapa) {
                const saved = await salvarEtapa(formEtapa, { validar: true });
                if (!saved) return;
            }

            if (etapa === 3) {
                const semExp = document.getElementById('semExperiencia');
                await fetch('/curriculo/salvar/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        etapa: 3,
                        sem_experiencia: semExp ? semExp.checked : false,
                    }),
                });
            }

            if (etapa === 4) {
                const semCur = document.getElementById('semCursos');
                await fetch('/curriculo/salvar/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        etapa: 4,
                        sem_cursos: semCur ? semCur.checked : false,
                    }),
                });
            }

            window.location.href = `?etapa=${etapa + 1}`;
        });
    }

    // Finalizar — valida só ao clicar
    if (btnFinalizar) {
        btnFinalizar.addEventListener('click', async function(e) {
            if (formEtapa) {
                e.preventDefault();
                limparErrosFormulario();
                const saved = await salvarEtapa(formEtapa, { validar: true });
                if (saved) window.location.href = this.href;
            }
        });
    }

    // Toggle sem experiência
    const semExp = document.getElementById('semExperiencia');
    if (semExp) {
        semExp.addEventListener('change', function() {
            document.getElementById('experienciasContainer').style.display =
                this.checked ? 'none' : 'block';
        });
    }

    // Toggle sem cursos
    const semCur = document.getElementById('semCursos');
    if (semCur) {
        semCur.addEventListener('change', function() {
            document.getElementById('cursosContainer').style.display =
                this.checked ? 'none' : 'block';
        });
    }

    // Form experiência
    const formExp = document.getElementById('formExperiencia');
    if (formExp) {
        formExp.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);

            const resp = await fetch('/curriculo/experiencia/adicionar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(data),
            });

            const result = await resp.json();
            if (result.success) {
                const exp = result.experiencia;
                const html = `
                    <div class="item-card" data-id="${exp.id}">
                        <button type="button" class="btn btn-sm btn-outline-danger btn-remove"
                                onclick="removerExperiencia(${exp.id})">
                            <i class="bi bi-x"></i>
                        </button>
                        <strong>${exp.cargo}</strong> — ${exp.empresa}<br>
                        <small class="text-muted">${exp.periodo}</small>
                        ${exp.descricao ? `<p class="mb-0 mt-1 small">${exp.descricao}</p>` : ''}
                    </div>`;
                document.getElementById('listaExperiencias').insertAdjacentHTML('beforeend', html);
                this.reset();
                showAutosave();
            }
        });
    }

    // Form curso
    const formCurso = document.getElementById('formCurso');
    if (formCurso) {
        formCurso.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);

            const resp = await fetch('/curriculo/curso/adicionar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(data),
            });

            const result = await resp.json();
            if (result.success) {
                const c = result.curso;
                const vazio = document.getElementById('cursosVazio');
                if (vazio) vazio.remove();
                const inst = c.instituicao ? ` — ${c.instituicao}` : '';
                const extra = [c.carga_horaria, c.ano].filter(Boolean).join(' | ');
                const html = `
                    <div class="item-card" data-id="${c.id}">
                        <button type="button" class="btn btn-sm btn-outline-danger btn-remove"
                                onclick="removerCurso(${c.id})">
                            <i class="bi bi-x"></i>
                        </button>
                        <strong>${c.nome}</strong>${inst}<br>
                        <small class="text-muted">${extra}</small>
                    </div>`;
                document.getElementById('listaCursos').insertAdjacentHTML('beforeend', html);
                const count = document.getElementById('cursosCount');
                if (count) count.textContent = document.querySelectorAll('#listaCursos .item-card').length;
                this.reset();
                this.querySelector('[name="nome"]')?.focus();
                showAutosave();
            } else {
                alert('Não foi possível adicionar. Verifique o nome do curso.');
            }
        });
    }
});

const LABELS_CAMPOS = {
    nome_completo: 'Nome completo',
    email: 'E-mail',
    telefone: 'Telefone',
    estado_civil: 'Estado civil',
    cidade: 'Cidade',
    bairro: 'Bairro',
    ano_nascimento: 'Ano de nascimento',
    escolaridade: 'Escolaridade',
    instituicao_escolaridade: 'Instituição',
    curso_escolaridade: 'Curso',
    ano_conclusao_escolaridade: 'Ano de conclusão',
    cnh: 'CNH',
    veiculo_proprio: 'Veículo próprio',
    objetivo_profissional: 'Objetivo profissional',
    sobre_mim: 'Sobre mim',
    habilidades: 'Habilidades',
    tema: 'Cor do currículo',
};

async function salvarRascunho(form) {
    const result = await enviarEtapa(form, { rascunho: true, validar: false });
    if (result.success) showAutosave();
}

async function salvarEtapa(form, options = {}) {
    const validar = options.validar !== false;
    const result = await enviarEtapa(form, { rascunho: false, validar });

    if (result.success) {
        if (!result.draft) showAutosave();
        return true;
    }

    if (validar && result.errors) {
        mostrarErrosFormulario(result.errors);
    }
    return false;
}

async function enviarEtapa(form, { rascunho, validar }) {
    const etapa = form.dataset.etapa;
    const formData = new FormData(form);
    formData.append('etapa', etapa);
    if (rascunho) formData.append('rascunho', '1');

    const resp = await fetch('/curriculo/salvar/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: formData,
    });

    return resp.json();
}

function limparErrosFormulario() {
    const box = document.getElementById('form-errors');
    if (box) {
        box.classList.add('d-none');
        box.innerHTML = '';
    }
    document.querySelectorAll('#form-etapa .is-invalid').forEach(el => {
        el.classList.remove('is-invalid');
    });
}

function mostrarErrosFormulario(errors) {
    let box = document.getElementById('form-errors');
    if (!box) {
        box = document.createElement('div');
        box.id = 'form-errors';
        box.className = 'alert alert-warning';
        const form = document.getElementById('form-etapa');
        form.parentNode.insertBefore(box, form);
    }

    const itens = [];
    for (const [field, msgs] of Object.entries(errors)) {
        const label = LABELS_CAMPOS[field] || field;
        itens.push(`<li><strong>${label}:</strong> ${msgs.join(', ')}</li>`);

        const input = document.querySelector(`#form-etapa [name="${field}"]`);
        if (input) input.classList.add('is-invalid');
    }

    box.innerHTML = `
        <div class="fw-semibold mb-2">Preencha os campos obrigatórios antes de continuar:</div>
        <ul class="mb-0 ps-3">${itens.join('')}</ul>
    `;
    box.classList.remove('d-none');
    box.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

async function removerExperiencia(id) {
    if (!confirm('Remover esta experiência?')) return;
    await fetch(`/curriculo/experiencia/${id}/remover/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
    });
    document.querySelector(`#listaExperiencias .item-card[data-id="${id}"]`).remove();
}

async function removerCurso(id) {
    if (!confirm('Remover este curso?')) return;
    await fetch(`/curriculo/curso/${id}/remover/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
    });
    document.querySelector(`#listaCursos .item-card[data-id="${id}"]`)?.remove();
    const count = document.getElementById('cursosCount');
    if (count) count.textContent = document.querySelectorAll('#listaCursos .item-card').length;
    showAutosave();
}
