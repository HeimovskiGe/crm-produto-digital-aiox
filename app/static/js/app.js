/* CRM Produto Digital - Base JS */

function showTab(tab) {
    document.querySelectorAll('.tab-content').forEach(function(el) {
        el.classList.remove('active');
    });
    document.querySelectorAll('.nav-btn').forEach(function(el) {
        el.classList.remove('active');
    });
    document.getElementById('tab-' + tab).classList.add('active');
    event.target.classList.add('active');
}

// Load dashboard stats (metricas reais de etapa_processo)
async function loadStats() {
    try {
        var resp = await fetch('/api/leads/metrics/resumo');
        if (resp.ok) {
            var data = await resp.json();
            document.getElementById('total-leads').textContent = data.total || 0;
            document.getElementById('leads-andamento').textContent = data.em_andamento || 0;
            document.getElementById('leads-fechado-ganho').textContent = data.fechado_ganho || 0;
            document.getElementById('conversion-rate').textContent = (data.taxa_conversao || 0) + '%';
        }
    } catch (e) {
        console.log('Metrics API error', e);
    }
}

document.addEventListener('DOMContentLoaded', loadStats);

/* ---- Painel de Intencao de Prospeccao ---- */

var ultimaAtividadeEm = null;

async function loadIntencao() {
    try {
        var resp = await fetch('/api/prospeccao/intencao');
        if (!resp.ok) return;
        var data = await resp.json();

        document.getElementById('intencao-feito').textContent = data.feito_hoje;
        var metaInput = document.getElementById('intencao-meta-input');
        if (document.activeElement !== metaInput) {
            metaInput.value = data.meta_hoje;
        }
        document.getElementById('intencao-streak').textContent = data.streak_dias;
        ultimaAtividadeEm = data.ultima_atividade_em ? new Date(data.ultima_atividade_em) : null;
        tickIntencao();
    } catch (e) {
        console.log('Intencao API error', e);
    }
}

async function updateMeta(value) {
    var meta = parseInt(value, 10) || 0;
    await fetch('/api/prospeccao/intencao/meta', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meta_atividades: meta })
    });
    await loadIntencao();
}

function pad2(n) {
    return String(n).padStart(2, '0');
}

function tickIntencao() {
    var bar = document.getElementById('intencao-bar');
    var tempoEl = document.getElementById('intencao-tempo');
    if (!bar || !tempoEl) return;

    if (!ultimaAtividadeEm) {
        tempoEl.textContent = 'nunca';
        bar.className = 'intencao-bar danger';
        return;
    }

    var diffSec = Math.max(0, Math.floor((Date.now() - ultimaAtividadeEm.getTime()) / 1000));
    var h = Math.floor(diffSec / 3600);
    var m = Math.floor((diffSec % 3600) / 60);
    var s = diffSec % 60;
    tempoEl.textContent = pad2(h) + ':' + pad2(m) + ':' + pad2(s);

    var minutosParado = diffSec / 60;
    var estado = 'ok';
    if (minutosParado >= 120) estado = 'danger';
    else if (minutosParado >= 30) estado = 'warn';
    bar.className = 'intencao-bar ' + estado;
}

document.addEventListener('DOMContentLoaded', function() {
    loadIntencao();
    setInterval(tickIntencao, 1000);
    setInterval(loadIntencao, 30000);
});

/* ---- Kanban de Leads (funil operacional - aulas Lucas Carmo) ---- */

var etapasCache = [];
var qualificacaoCache = [];
var leadsCache = [];

async function loadStages() {
    var resp = await fetch('/api/leads/meta/etapas-processo');
    etapasCache = await resp.json();
}

async function loadQualificacao() {
    var resp = await fetch('/api/leads/meta/qualificacao');
    qualificacaoCache = await resp.json();
}

function qualificacaoLabel(pipelineStage) {
    var found = qualificacaoCache.find(function(q) { return q.value === pipelineStage; });
    return found ? found.label : pipelineStage;
}

async function loadLeads() {
    var resp = await fetch('/api/leads');
    leadsCache = await resp.json();
    renderKanban();
}

function renderKanban() {
    var board = document.getElementById('kanban-board');
    if (!board) return;
    board.innerHTML = '';

    etapasCache.forEach(function(etapa) {
        var leadsInEtapa = leadsCache.filter(function(l) { return l.etapa_processo === etapa.value; });

        var col = document.createElement('div');
        col.className = 'kanban-col';

        var header = document.createElement('h3');
        header.textContent = etapa.label + ' (' + leadsInEtapa.length + ')';
        col.appendChild(header);

        col.dataset.stage = etapa.value;
        col.addEventListener('dragover', onDragOver);
        col.addEventListener('dragleave', onDragLeave);
        col.addEventListener('drop', onDrop);

        var cardsEl = document.createElement('div');
        cardsEl.className = 'kanban-cards';

        leadsInEtapa.forEach(function(lead) {
            var card = document.createElement('div');
            card.className = 'kanban-card';
            card.draggable = true;
            card.dataset.leadId = lead.id;
            card.addEventListener('dragstart', onDragStart);
            card.addEventListener('dragend', onDragEnd);

            var nome = document.createElement('strong');
            nome.textContent = lead.nome;
            card.appendChild(nome);

            if (lead.empresa) {
                var empresa = document.createElement('small');
                empresa.textContent = lead.empresa;
                card.appendChild(document.createElement('br'));
                card.appendChild(empresa);
            }

            var tag = document.createElement('div');
            tag.className = 'tags';
            var badge = document.createElement('span');
            badge.className = 'tag';
            badge.textContent = qualificacaoLabel(lead.pipeline_stage);
            tag.appendChild(badge);
            card.appendChild(tag);

            var logBtn = document.createElement('button');
            logBtn.type = 'button';
            logBtn.className = 'btn-log-atividade';
            logBtn.textContent = '+ Atividade';
            logBtn.addEventListener('click', function(ev) {
                ev.stopPropagation();
                toggleAtividadeForm(lead.id, card);
            });
            card.appendChild(logBtn);

            cardsEl.appendChild(card);
        });

        col.appendChild(cardsEl);
        board.appendChild(col);
    });
}

var CANAL_OPTIONS = [
    ['telefone', 'Telefone'], ['presencial', 'Presencial'], ['email', 'E-mail'],
    ['venda_social', 'Venda social'], ['mensagem_texto', 'Mensagem de texto'],
    ['referencia', 'Referencia'], ['networking', 'Networking'],
    ['indicacao_interna', 'Indicacao interna'], ['feira_comercial', 'Feira comercial'],
    ['chamada_fria', 'Chamada fria']
];
var OBJETIVO_OPTIONS = [
    ['marcar_reuniao', 'Marcar reuniao'], ['qualificar_informacao', 'Qualificar informacao'],
    ['construir_familiaridade', 'Construir familiaridade'], ['assentamento', 'Assentamento'],
    ['fechar_venda', 'Fechar venda']
];

function buildSelect(className, options) {
    var select = document.createElement('select');
    select.className = className;
    options.forEach(function(opt) {
        var el = document.createElement('option');
        el.value = opt[0];
        el.textContent = opt[1];
        select.appendChild(el);
    });
    return select;
}

function toggleAtividadeForm(leadId, card) {
    var existing = card.querySelector('.atividade-form');
    if (existing) { existing.remove(); return; }

    var form = document.createElement('div');
    form.className = 'atividade-form';

    var canalSelect = buildSelect('at-canal', CANAL_OPTIONS);
    var objetivoSelect = buildSelect('at-objetivo', OBJETIVO_OPTIONS);
    var saveBtn = document.createElement('button');
    saveBtn.type = 'button';
    saveBtn.className = 'btn-primary';
    saveBtn.textContent = 'Salvar';

    saveBtn.addEventListener('click', async function() {
        saveBtn.disabled = true;
        await fetch('/api/leads/' + leadId + '/atividades', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                canal: canalSelect.value,
                objetivo_contato: objetivoSelect.value,
                data_hora: new Date().toISOString()
            })
        });
        await loadLeads();
        await loadIntencao();
    });

    form.appendChild(canalSelect);
    form.appendChild(objetivoSelect);
    form.appendChild(saveBtn);
    card.appendChild(form);
}

function onDragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.dataset.leadId);
    e.target.classList.add('dragging');
}

function onDragEnd(e) {
    e.target.classList.remove('dragging');
}

function onDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function onDragLeave(e) {
    e.currentTarget.classList.remove('dragover');
}

async function onDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    var leadId = e.dataTransfer.getData('text/plain');
    var newStage = e.currentTarget.dataset.stage;
    await fetch('/api/leads/' + leadId, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ etapa_processo: newStage })
    });
    await loadLeads();
}

function toggleNewLeadForm(show) {
    var form = document.getElementById('new-lead-form');
    if (form) form.classList.toggle('open', show);
}

async function createLead(event) {
    event.preventDefault();
    var form = event.target;
    var payload = {
        nome: form.nome.value,
        empresa: form.empresa.value || null,
        telefone: form.telefone.value || null,
        email: form.email.value || null
    };
    var resp = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    if (resp.ok) {
        form.reset();
        toggleNewLeadForm(false);
        await loadLeads();
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    await Promise.all([loadStages(), loadQualificacao()]);
    await loadLeads();
});
