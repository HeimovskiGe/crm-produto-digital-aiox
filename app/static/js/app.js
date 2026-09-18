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

/* ---- Rotulo legivel pro CNAE (raw code nao diz nada sobre "quem e" o lead) ----
   Cobre os CNAEs mais frequentes nas bases do pam-geh (~75% dos leads
   amostrados); o que nao estiver aqui cai no fallback (mostra o codigo cru).
   Fonte: IBGE/Concla - descricoes oficiais das subclasses CNAE 2.0/2.3. */
var CNAE_LABELS = {
    '4781-4/00': 'Comercio varejista de artigos do vestuario e acessorios',
    '9602-5/01': 'Cabeleireiros, manicure e pedicure',
    '9602-5/02': 'Estetica e outros cuidados de beleza',
    '9491000': 'Organizacao religiosa ou filosofica',
    '1091-1/02': 'Padaria e confeitaria (producao propria)',
    '3101-2/00': 'Fabricacao de moveis de madeira',
    '2539-0/01': 'Usinagem, tornearia e solda',
    '1412-6/01': 'Confeccao de vestuario (serie)',
    '4399-1/03': 'Obras de alvenaria',
    '1412-6/02': 'Confeccao de vestuario sob medida',
    '2542-0/00': 'Serralheria (exceto esquadrias)',
    '0161-0/03': 'Preparacao de terreno, cultivo e colheita',
    '2512-8/00': 'Fabricacao de esquadrias de metal',
    '4930-2/02': 'Transporte rodoviario de carga',
    '7319-0/02': 'Promocao de vendas',
    '5611-2/03': 'Lanchonete, casa de sucos/cha',
    '1359-6/00': 'Fabricacao de outros produtos texteis',
    '1091-1/01': 'Panificacao industrial',
    '4520-0/01': 'Manutencao e reparacao mecanica de veiculos',
    '5611-2/04': 'Bar (sem entretenimento)',
    '4530-7/03': 'Comercio de pecas/acessorios de veiculos',
    '2391-5/03': 'Trabalhos em marmore, granito e outras pedras',
    '4321-5/00': 'Instalacao e manutencao eletrica',
    '4712-1/00': 'Minimercado, mercearia ou armazem',
    '2342-7/02': 'Fabricacao de ceramica/barro pra construcao',
};

function cnaeLabel(code) {
    if (!code) return null;
    return CNAE_LABELS[code] || code;
}

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
          try {
            var card = document.createElement('div');
            card.className = 'kanban-card';
            card.draggable = true;
            card.dataset.leadId = lead.id;
            card.addEventListener('dragstart', onDragStart);
            card.addEventListener('dragend', onDragEnd);
            card.addEventListener('click', function(ev) {
                if (ev.target.closest('button, select, input, a')) return;
                openLeadModal(lead.id);
            });

            var nome = document.createElement('strong');
            nome.textContent = lead.nome;
            card.appendChild(nome);

            if (lead.empresa && lead.empresa !== lead.nome) {
                var empresa = document.createElement('small');
                empresa.textContent = lead.empresa;
                card.appendChild(document.createElement('br'));
                card.appendChild(empresa);
            }

            var metaPartes = [lead.territorio, cnaeLabel(lead.vertical), lead.telefone].filter(Boolean);
            if (metaPartes.length) {
                var meta = document.createElement('small');
                meta.className = 'card-meta';
                meta.textContent = metaPartes.join(' · ');
                card.appendChild(document.createElement('br'));
                card.appendChild(meta);
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

            var reuniaoBtn = document.createElement('button');
            reuniaoBtn.type = 'button';
            reuniaoBtn.className = 'btn-log-atividade';
            reuniaoBtn.textContent = '📋 Reuniao / Roteiro';
            reuniaoBtn.addEventListener('click', function(ev) {
                ev.stopPropagation();
                openLeadModal(lead.id);
            });
            card.appendChild(reuniaoBtn);

            var moverSelect = buildMoverEtapaSelect(lead);
            card.appendChild(moverSelect);

            cardsEl.appendChild(card);
          } catch (e) {
            console.error('Erro ao renderizar lead ' + lead.id, e);
          }
        });

        col.appendChild(cardsEl);
        board.appendChild(col);
    });
}

function buildMoverEtapaSelect(lead) {
    var select = document.createElement('select');
    select.className = 'mover-select';
    etapasCache.forEach(function(etapa) {
        var opt = document.createElement('option');
        opt.value = etapa.value;
        opt.textContent = 'Mover para: ' + etapa.label;
        if (etapa.value === lead.etapa_processo) opt.selected = true;
        select.appendChild(opt);
    });
    select.addEventListener('click', function(ev) { ev.stopPropagation(); });
    select.addEventListener('change', async function() {
        await fetch('/api/leads/' + lead.id, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ etapa_processo: select.value })
        });
        await loadLeads();
    });
    return select;
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

/* ---- Empresarios (bases pam-geh - sem migrar, direto na fonte) ---- */

var fontesCache = [];
var statusColumnsCache = [];
var fonteAtual = null;
var empresariosPorStatus = {};

async function loadFontes() {
    var fontesResp = await fetch('/api/empresarios/meta/fontes');
    fontesCache = await fontesResp.json();
    var statusResp = await fetch('/api/empresarios/meta/status');
    statusColumnsCache = await statusResp.json();

    var selector = document.getElementById('fonte-selector');
    if (!selector) return;
    selector.innerHTML = '';
    fontesCache.forEach(function(f, idx) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'nav-btn' + (idx === 0 ? ' active' : '');
        btn.textContent = f.label;
        btn.addEventListener('click', function() { selectFonte(f.value, btn); });
        selector.appendChild(btn);
    });
    if (fontesCache.length) selectFonte(fontesCache[0].value, selector.firstChild);
}

function selectFonte(fonte, btnEl) {
    fonteAtual = fonte;
    document.querySelectorAll('#fonte-selector .nav-btn').forEach(function(b) { b.classList.remove('active'); });
    if (btnEl) btnEl.classList.add('active');
    reloadFonteAtual();
}

function reloadFonteAtual() {
    empresariosPorStatus = {};
    statusColumnsCache.forEach(function(s) { empresariosPorStatus[s.value] = { items: [], total: 0, offset: 0 }; });
    renderEmpresariosBoard();
    statusColumnsCache.forEach(function(s) { loadEmpresariosColuna(s.value); });
}

async function loadEmpresariosColuna(status) {
    var state = empresariosPorStatus[status];
    var resp = await fetch('/api/empresarios/' + fonteAtual + '?status=' + status + '&limit=30&offset=' + state.offset);
    if (!resp.ok) return;
    var data = await resp.json();
    state.items = state.items.concat(data.items);
    state.total = data.total;
    state.offset = state.items.length;
    renderEmpresariosBoard();
}

function renderEmpresariosBoard() {
    var board = document.getElementById('empresarios-board');
    if (!board) return;
    board.innerHTML = '';

    statusColumnsCache.forEach(function(statusCol) {
        var state = empresariosPorStatus[statusCol.value] || { items: [], total: 0 };

        var col = document.createElement('div');
        col.className = 'kanban-col';
        col.dataset.stage = statusCol.value;
        col.addEventListener('dragover', onDragOver);
        col.addEventListener('dragleave', onDragLeave);
        col.addEventListener('drop', onDropEmp);

        var header = document.createElement('h3');
        header.textContent = statusCol.label + ' (' + state.total + ')';
        col.appendChild(header);

        var cardsEl = document.createElement('div');
        cardsEl.className = 'kanban-cards';

        state.items.forEach(function(item) {
            var card = document.createElement('div');
            card.className = 'kanban-card';
            card.draggable = true;
            card.dataset.empId = item.id;
            card.addEventListener('dragstart', onDragStartEmp);
            card.addEventListener('dragend', onDragEnd);

            var nome = document.createElement('strong');
            nome.textContent = item.razao_social || item.nome_fantasia || '(sem nome)';
            card.appendChild(nome);

            var meta = document.createElement('small');
            meta.className = 'card-meta';
            var localParte = [item.bairro, item.municipio].filter(Boolean).join(', ');
            meta.textContent = [item.telefone, localParte, cnaeLabel(item.cnae)].filter(Boolean).join(' · ');
            card.appendChild(document.createElement('br'));
            card.appendChild(meta);

            if (item.whatsapp) {
                var waLink = document.createElement('a');
                waLink.href = 'https://wa.me/' + item.whatsapp;
                waLink.target = '_blank';
                waLink.rel = 'noopener';
                waLink.className = 'btn-log-atividade';
                waLink.style.display = 'block';
                waLink.style.textAlign = 'center';
                waLink.style.textDecoration = 'none';
                waLink.textContent = '💬 WhatsApp';
                card.appendChild(waLink);
            }

            var prospectarBtn = document.createElement('button');
            prospectarBtn.type = 'button';
            prospectarBtn.className = 'btn-primary';
            prospectarBtn.style.width = '100%';
            prospectarBtn.style.marginTop = '6px';
            prospectarBtn.style.marginBottom = '0';
            prospectarBtn.style.fontSize = '0.75rem';
            prospectarBtn.style.padding = '0.35rem';
            prospectarBtn.textContent = '+ Prospectar';
            prospectarBtn.addEventListener('click', function() {
                prospectarEmpresario(fonteAtual, item, prospectarBtn);
            });
            card.appendChild(prospectarBtn);

            card.appendChild(buildMoverStatusSelect(fonteAtual, item, statusCol.value));

            cardsEl.appendChild(card);
        });

        if (state.items.length < state.total) {
            var moreBtn = document.createElement('button');
            moreBtn.type = 'button';
            moreBtn.className = 'btn-secondary';
            moreBtn.style.width = '100%';
            moreBtn.style.marginTop = '0.5rem';
            moreBtn.textContent = 'Carregar mais (' + state.items.length + '/' + state.total + ')';
            moreBtn.addEventListener('click', function() { loadEmpresariosColuna(statusCol.value); });
            cardsEl.appendChild(moreBtn);
        }

        col.appendChild(cardsEl);
        board.appendChild(col);
    });
}

function buildMoverStatusSelect(fonte, item, statusAtual) {
    var select = document.createElement('select');
    select.className = 'mover-select';
    statusColumnsCache.forEach(function(s) {
        var opt = document.createElement('option');
        opt.value = s.value;
        opt.textContent = 'Mover para: ' + s.label;
        if (s.value === statusAtual) opt.selected = true;
        select.appendChild(opt);
    });
    select.addEventListener('click', function(ev) { ev.stopPropagation(); });
    select.addEventListener('change', async function() {
        await fetch('/api/empresarios/' + fonte + '/' + item.id, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: select.value })
        });
        reloadFonteAtual();
    });
    return select;
}

function onDragStartEmp(e) {
    e.dataTransfer.setData('text/plain', e.target.dataset.empId);
    e.target.classList.add('dragging');
}

async function onDropEmp(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    var empId = e.dataTransfer.getData('text/plain');
    var newStatus = e.currentTarget.dataset.stage;
    await fetch('/api/empresarios/' + fonteAtual + '/' + empId, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    });
    reloadFonteAtual();
}

document.addEventListener('DOMContentLoaded', loadFontes);

/* ---- Configuracoes (produto/oferta) ---- */

async function loadProduto() {
    var form = document.getElementById('produto-form');
    if (!form) return;
    var resp = await fetch('/api/produto');
    if (!resp.ok) return;
    var data = await resp.json();
    Object.keys(data).forEach(function(key) {
        if (form.elements[key] && data[key] != null) {
            form.elements[key].value = data[key];
        }
    });
}

async function saveProduto(event) {
    event.preventDefault();
    var form = event.target;
    var payload = {
        nome_produto: form.nome_produto.value || null,
        proposta_valor: form.proposta_valor.value || null,
        dor_resolvida: form.dor_resolvida.value || null,
        entregavel_1: form.entregavel_1.value || null,
        entregavel_2: form.entregavel_2.value || null,
        entregavel_3: form.entregavel_3.value || null,
        faixa_preco: form.faixa_preco.value || null
    };
    var resp = await fetch('/api/produto', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    if (resp.ok) alert('Produto salvo.');
}

document.addEventListener('DOMContentLoaded', loadProduto);

/* ---- Google Calendar (horarios livres pra agendar Reuniao de Venda) ---- */

async function loadAgendaStatus() {
    var container = document.getElementById('agenda-status');
    if (!container) return;
    container.innerHTML = 'Carregando...';
    var resp = await fetch('/api/agenda/status');
    var data = await resp.json();
    container.innerHTML = '';

    if (data.conectado) {
        var msg = document.createElement('p');
        msg.style.color = 'var(--primary)';
        msg.style.marginBottom = '0.5rem';
        msg.textContent = '✓ Conectado';
        container.appendChild(msg);

        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn-secondary';
        btn.textContent = 'Desconectar';
        btn.addEventListener('click', async function() {
            await fetch('/api/agenda/desconectar', { method: 'POST' });
            await loadAgendaStatus();
        });
        container.appendChild(btn);
    } else {
        var link = document.createElement('a');
        link.href = '/api/agenda/conectar';
        link.className = 'btn-primary';
        link.style.display = 'inline-block';
        link.style.textDecoration = 'none';
        link.textContent = 'Conectar Google Calendar';
        container.appendChild(link);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    loadAgendaStatus();
    var params = new URLSearchParams(window.location.search);
    if (params.has('agenda')) {
        if (params.get('agenda') === 'conectado') {
            alert('Google Calendar conectado.');
        } else {
            alert('Erro ao conectar Google Calendar: ' + (params.get('motivo') || 'desconhecido'));
        }
        history.replaceState({}, '', window.location.pathname);
    }
});

/* ---- Prospectar (Empresario -> Lead real) ---- */

async function prospectarEmpresario(fonte, item, btnEl) {
    btnEl.disabled = true;
    btnEl.textContent = 'Prospectando...';
    var resp = await fetch('/api/empresarios/' + fonte + '/' + item.id + '/prospectar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            nome_fantasia: item.nome_fantasia,
            razao_social: item.razao_social,
            telefone: item.telefone,
            whatsapp: item.whatsapp,
            email: item.email,
            municipio: item.municipio,
            bairro: item.bairro,
            cnae: item.cnae
        })
    });
    if (resp.ok) {
        btnEl.textContent = '✓ Em Leads';
        reloadFonteAtual();
        loadLeads();
    } else {
        btnEl.disabled = false;
        btnEl.textContent = '+ Prospectar';
    }
}

/* ---- Modal do Lead: info + Reuniao de Venda (7 Passos) + Referidos ---- */

var ETAPA_REUNIAO_ORDEM = ['apresentacao', 'conexao', 'decisao_imediata', 'showtime', 'fechamento', 'referidos', 'validacao'];

var modalState = null; // { leadId, lead, roteiro, reuniao }

function closeLeadModal() {
    document.getElementById('lead-modal').classList.remove('open');
    modalState = null;
}

async function openLeadModal(leadId) {
    var modal = document.getElementById('lead-modal');
    var box = document.getElementById('lead-modal-box');
    box.innerHTML = 'Carregando...';
    modal.classList.add('open');

    try {
        var lead = leadsCache.find(function(l) { return l.id === leadId; });
        var roteiroResp = await fetch('/api/leads/' + leadId + '/roteiro');
        if (!roteiroResp.ok) throw new Error('roteiro respondeu ' + roteiroResp.status);
        var roteiro = await roteiroResp.json();
        var reuniaoResp = await fetch('/api/leads/' + leadId + '/reunioes/atual');
        var reuniao = reuniaoResp.ok ? await reuniaoResp.json() : null;

        modalState = { leadId: leadId, lead: lead, roteiro: roteiro, reuniao: reuniao };
        await renderLeadModal();
    } catch (e) {
        console.error('Erro ao abrir modal do lead ' + leadId, e);
        box.innerHTML = '';
        var err = document.createElement('p');
        err.style.color = 'var(--destructive)';
        err.textContent = 'Erro ao carregar este lead: ' + (e && e.message ? e.message : e);
        box.appendChild(err);
        var closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.className = 'btn-secondary';
        closeBtn.textContent = 'Fechar';
        closeBtn.addEventListener('click', closeLeadModal);
        box.appendChild(closeBtn);
    }
}

function leadInfoItem(label, value, link) {
    var d = document.createElement('div');
    var s = document.createElement('span');
    s.textContent = label;
    d.appendChild(s);
    if (value && link) {
        var a = document.createElement('a');
        a.href = link;
        a.target = '_blank';
        a.rel = 'noopener';
        a.textContent = value;
        d.appendChild(a);
    } else {
        d.appendChild(document.createTextNode(value || '-'));
    }
    return d;
}

async function renderAgendaSection(box, leadId) {
    var wrap = document.createElement('div');
    wrap.style.marginBottom = '1rem';

    var toggleBtn = document.createElement('button');
    toggleBtn.type = 'button';
    toggleBtn.className = 'btn-secondary';
    toggleBtn.style.width = '100%';
    toggleBtn.textContent = '📅 Agendar Reuniao (ver horarios livres)';

    var slotsWrap = document.createElement('div');
    slotsWrap.style.display = 'none';
    slotsWrap.style.marginTop = '0.5rem';

    toggleBtn.addEventListener('click', async function() {
        var abrindo = slotsWrap.style.display === 'none';
        slotsWrap.style.display = abrindo ? 'block' : 'none';
        if (!abrindo) return;

        slotsWrap.textContent = 'Carregando horarios...';
        var statusResp = await fetch('/api/agenda/status');
        var statusData = await statusResp.json();
        if (!statusData.conectado) {
            slotsWrap.innerHTML = '';
            var msg = document.createElement('p');
            msg.className = 'roteiro-objetivo';
            msg.textContent = 'Conecte sua conta do Google em Configuracoes pra ver horarios livres.';
            slotsWrap.appendChild(msg);
            return;
        }

        var resp = await fetch('/api/agenda/horarios-livres?dias=3');
        if (!resp.ok) {
            slotsWrap.innerHTML = '';
            var err = document.createElement('p');
            err.style.color = 'var(--destructive)';
            err.textContent = 'Erro ao buscar horarios livres.';
            slotsWrap.appendChild(err);
            return;
        }
        var slots = await resp.json();
        slotsWrap.innerHTML = '';
        if (!slots.length) {
            slotsWrap.textContent = 'Nenhum horario livre encontrado nos proximos dias.';
            return;
        }

        var lista = document.createElement('div');
        lista.style.display = 'flex';
        lista.style.flexWrap = 'wrap';
        lista.style.gap = '0.4rem';
        slots.slice(0, 24).forEach(function(slot) {
            var slotBtn = document.createElement('button');
            slotBtn.type = 'button';
            slotBtn.className = 'btn-secondary';
            slotBtn.style.margin = '0';
            slotBtn.style.fontSize = '0.72rem';
            var d = new Date(slot.inicio);
            slotBtn.textContent = d.toLocaleString('pt-BR', {
                weekday: 'short', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
            });
            slotBtn.addEventListener('click', async function() {
                slotBtn.disabled = true;
                slotBtn.textContent = 'Agendando...';
                var criarResp = await fetch('/api/agenda/eventos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ lead_id: leadId, inicio: slot.inicio, fim: slot.fim })
                });
                if (criarResp.ok) {
                    slotBtn.textContent = '✓ Agendado';
                } else {
                    slotBtn.disabled = false;
                    slotBtn.textContent = 'Erro, tenta de novo';
                }
            });
            lista.appendChild(slotBtn);
        });
        slotsWrap.appendChild(lista);
    });

    wrap.appendChild(toggleBtn);
    wrap.appendChild(slotsWrap);
    box.appendChild(wrap);
}

async function renderLeadModal() {
    var box = document.getElementById('lead-modal-box');
    box.innerHTML = '';
    var st = modalState;
    if (!st) return;
    var lead = st.lead;

    var header = document.createElement('div');
    header.className = 'modal-header';
    var titleWrap = document.createElement('div');
    var h3 = document.createElement('h3');
    h3.textContent = lead ? lead.nome : ('Lead #' + st.leadId);
    titleWrap.appendChild(h3);
    if (lead && lead.empresa && lead.empresa !== lead.nome) {
        var sub = document.createElement('small');
        sub.textContent = lead.empresa;
        titleWrap.appendChild(sub);
    }
    header.appendChild(titleWrap);
    var closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'modal-close';
    closeBtn.textContent = '×';
    closeBtn.addEventListener('click', closeLeadModal);
    header.appendChild(closeBtn);
    box.appendChild(header);

    if (lead) {
        var grid = document.createElement('div');
        grid.className = 'lead-info-grid';
        var waLink = lead.telefone ? 'https://wa.me/' + lead.telefone.replace(/\D/g, '') : null;
        grid.appendChild(leadInfoItem('Telefone', lead.telefone, waLink));
        grid.appendChild(leadInfoItem('E-mail', lead.email));
        grid.appendChild(leadInfoItem('Territorio', lead.territorio));
        grid.appendChild(leadInfoItem('Vertical', cnaeLabel(lead.vertical)));
        grid.appendChild(leadInfoItem('Qualificacao', qualificacaoLabel(lead.pipeline_stage)));
        grid.appendChild(leadInfoItem('Tentativas de contato', String(lead.tentativas_contato)));
        box.appendChild(grid);
    }

    await renderAgendaSection(box, st.leadId);

    if (!st.reuniao) {
        var startBtn = document.createElement('button');
        startBtn.type = 'button';
        startBtn.className = 'btn-primary';
        startBtn.style.width = '100%';
        startBtn.textContent = '▶ Iniciar Reuniao de Venda (7 Passos)';
        startBtn.addEventListener('click', async function() {
            var resp = await fetch('/api/leads/' + st.leadId + '/reunioes', { method: 'POST' });
            st.reuniao = await resp.json();
            await loadLeads();
            await renderLeadModal();
        });
        box.appendChild(startBtn);
        return;
    }

    var reuniao = st.reuniao;

    var nav = document.createElement('div');
    nav.className = 'etapa-nav';
    ETAPA_REUNIAO_ORDEM.forEach(function(etapaKey, idx) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'etapa-btn' + (etapaKey === reuniao.etapa_atual ? ' active' : '');
        btn.textContent = idx + 1;
        btn.title = etapaKey;
        btn.addEventListener('click', async function() {
            var resp = await fetch('/api/reunioes/' + reuniao.id, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ etapa_atual: etapaKey })
            });
            st.reuniao = await resp.json();
            await renderLeadModal();
        });
        nav.appendChild(btn);
    });
    box.appendChild(nav);

    var passoAtual = st.roteiro.find(function(p) { return p.etapa === reuniao.etapa_atual; });
    if (passoAtual) {
        var titulo = document.createElement('strong');
        titulo.textContent = passoAtual.titulo;
        box.appendChild(titulo);

        var objetivo = document.createElement('p');
        objetivo.className = 'roteiro-objetivo';
        objetivo.textContent = passoAtual.objetivo;
        box.appendChild(objetivo);

        var lista = document.createElement('ul');
        lista.className = 'roteiro-perguntas';
        passoAtual.perguntas.forEach(function(p) {
            var li = document.createElement('li');
            li.textContent = p;
            lista.appendChild(li);
        });
        box.appendChild(lista);
    }

    if (reuniao.etapa_atual === 'decisao_imediata' && !reuniao.di_confirmada) {
        var diBtn = document.createElement('button');
        diBtn.type = 'button';
        diBtn.className = 'btn-primary';
        diBtn.style.width = '100%';
        diBtn.textContent = 'Confirmar DI (topou sim/nao no final)';
        diBtn.addEventListener('click', async function() {
            var resp = await fetch('/api/reunioes/' + reuniao.id, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ di_confirmada: true })
            });
            st.reuniao = await resp.json();
            await renderLeadModal();
        });
        box.appendChild(diBtn);
    }

    if (reuniao.etapa_atual === 'referidos' || reuniao.etapa_atual === 'validacao') {
        await renderReferidosSection(box, st.leadId, reuniao.etapa_atual);
    }

    if (!reuniao.resultado) {
        var fecharRow = document.createElement('div');
        fecharRow.className = 'fechar-row';

        var valorInput = document.createElement('input');
        valorInput.type = 'number';
        valorInput.placeholder = 'Valor fechado';

        var ganhoBtn = document.createElement('button');
        ganhoBtn.type = 'button';
        ganhoBtn.className = 'btn-primary';
        ganhoBtn.textContent = '✓ Ganho';
        ganhoBtn.addEventListener('click', async function() {
            await fetch('/api/reunioes/' + reuniao.id, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ resultado: 'ganho', valor_fechado: parseFloat(valorInput.value) || null })
            });
            await loadLeads();
            closeLeadModal();
        });

        var perdidoBtn = document.createElement('button');
        perdidoBtn.type = 'button';
        perdidoBtn.className = 'btn-secondary';
        perdidoBtn.textContent = '✗ Perdido';
        perdidoBtn.addEventListener('click', async function() {
            await fetch('/api/reunioes/' + reuniao.id, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ resultado: 'perdido' })
            });
            await loadLeads();
            closeLeadModal();
        });

        fecharRow.appendChild(valorInput);
        fecharRow.appendChild(ganhoBtn);
        fecharRow.appendChild(perdidoBtn);
        box.appendChild(fecharRow);
    }
}

async function renderReferidosSection(box, leadId, etapaAtual) {
    var wrap = document.createElement('div');

    var subtitle = document.createElement('strong');
    subtitle.textContent = etapaAtual === 'referidos'
        ? 'Referidos pegos nesta ligacao (pegue de 5 a 10, na hora)'
        : 'Validacao - mensagem de pre-aviso enviada pro indicado?';
    wrap.appendChild(subtitle);

    var resp = await fetch('/api/leads/' + leadId + '/referidos');
    var referidos = resp.ok ? await resp.json() : [];

    var lista = document.createElement('ul');
    lista.className = 'referidos-lista';
    referidos.forEach(function(r) {
        var li = document.createElement('li');
        var info = document.createElement('span');
        info.textContent = r.nome_indicado + ' · ' + r.contato_indicado;
        li.appendChild(info);

        var label = document.createElement('label');
        var checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = r.mensagem_validacao_enviada;
        checkbox.addEventListener('change', async function() {
            await fetch('/api/referidos/' + r.id, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mensagem_validacao_enviada: checkbox.checked })
            });
        });
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode('validado'));
        li.appendChild(label);
        lista.appendChild(li);
    });
    wrap.appendChild(lista);

    if (etapaAtual === 'referidos') {
        var form = document.createElement('div');
        form.className = 'referidos-form';
        var nomeInput = document.createElement('input');
        nomeInput.placeholder = 'Nome do indicado';
        var contatoInput = document.createElement('input');
        contatoInput.placeholder = 'Contato (telefone/whatsapp)';
        var addBtn = document.createElement('button');
        addBtn.type = 'button';
        addBtn.className = 'btn-primary';
        addBtn.style.margin = '0';
        addBtn.textContent = '+ Adicionar';
        addBtn.addEventListener('click', async function() {
            if (!nomeInput.value || !contatoInput.value) return;
            await fetch('/api/leads/' + leadId + '/referidos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nome_indicado: nomeInput.value, contato_indicado: contatoInput.value })
            });
            await renderLeadModal();
        });
        form.appendChild(nomeInput);
        form.appendChild(contatoInput);
        form.appendChild(addBtn);
        wrap.appendChild(form);
    }

    box.appendChild(wrap);
}
