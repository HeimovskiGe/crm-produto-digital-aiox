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

// Load dashboard stats
async function loadStats() {
    try {
        var resp = await fetch('/api/metrics/summary');
        if (resp.ok) {
            var data = await resp.json();
            document.getElementById('total-students').textContent = data.total_students || 0;
            document.getElementById('total-leads').textContent = data.total_leads || 0;
            document.getElementById('total-orders').textContent = data.total_orders || 0;
            document.getElementById('conversion-rate').textContent = (data.conversion_rate || 0) + '%';
        }
    } catch (e) {
        console.log('Metrics API not yet implemented');
    }
}

document.addEventListener('DOMContentLoaded', loadStats);

/* ---- Kanban de Leads (Piramide da Prospeccao) ---- */

var stagesCache = [];
var leadsCache = [];

async function loadStages() {
    var resp = await fetch('/api/leads/meta/stages');
    stagesCache = await resp.json();
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

    stagesCache.forEach(function(stage) {
        var leadsInStage = leadsCache.filter(function(l) { return l.pipeline_stage === stage.value; });

        var col = document.createElement('div');
        col.className = 'kanban-col';

        var header = document.createElement('h3');
        header.textContent = stage.label + ' (' + leadsInStage.length + ')';
        col.appendChild(header);

        var cardsEl = document.createElement('div');
        cardsEl.className = 'kanban-cards';
        cardsEl.dataset.stage = stage.value;
        cardsEl.addEventListener('dragover', onDragOver);
        cardsEl.addEventListener('drop', onDrop);

        leadsInStage.forEach(function(lead) {
            var card = document.createElement('div');
            card.className = 'kanban-card';
            card.draggable = true;
            card.dataset.leadId = lead.id;
            card.addEventListener('dragstart', onDragStart);

            var nome = document.createElement('strong');
            nome.textContent = lead.nome;
            card.appendChild(nome);

            if (lead.empresa) {
                var empresa = document.createElement('small');
                empresa.textContent = lead.empresa;
                card.appendChild(document.createElement('br'));
                card.appendChild(empresa);
            }

            cardsEl.appendChild(card);
        });

        col.appendChild(cardsEl);
        board.appendChild(col);
    });
}

function onDragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.dataset.leadId);
}

function onDragOver(e) {
    e.preventDefault();
}

async function onDrop(e) {
    e.preventDefault();
    var leadId = e.dataTransfer.getData('text/plain');
    var newStage = e.currentTarget.dataset.stage;
    await fetch('/api/leads/' + leadId, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pipeline_stage: newStage })
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
    await loadStages();
    await loadLeads();
});
