let estadoAtual = {
    superarea: null,
    area: null,
    aba: null
};

// ================= INICIALIZAÇÃO =================
window.addEventListener('DOMContentLoaded', async () => {
    const config = await eel.get_config_iniciais()();
    
    document.getElementById('app-title').innerText = config.titulo;
    document.getElementById('sys-date').innerText = config.data_atual;

    const topMenu = document.getElementById('top-menu-container');
    config.superareas.forEach(nome => {
        const btn = document.createElement('button');
        btn.className = 'btn-top';
        btn.innerText = nome;
        btn.onclick = () => selecionarSuperarea(nome, btn);
        topMenu.appendChild(btn);
    });

    setInterval(atualizarLogs, 2000);
});

// ================= NAVEGAÇÃO =================
async function selecionarSuperarea(nome, btnElement) {
    estadoAtual.superarea = nome;
    
    document.querySelectorAll('.btn-top').forEach(b => b.classList.remove('active'));
    btnElement.classList.add('active');
    document.getElementById('current-superarea-badge').innerText = nome;
    document.getElementById('current-area-title').innerText = "Carregando...";

    const areas = await eel.get_areas(nome)();
    montarMenuLateral(areas);
}

// ATUALIZADO: Lógica de Accordion implementada
async function montarMenuLateral(areas) {
    const container = document.getElementById('side-menu-container');
    container.innerHTML = ''; 

    if (areas.length === 0) {
        container.innerHTML = '<div class="empty-state">Nenhuma área configurada.</div>';
        document.getElementById('current-area-title').innerText = "Vazio";
        return;
    }

    for (let i = 0; i < areas.length; i++) {
        const areaNome = areas[i];
        
        if (i === 0) {
            document.getElementById('current-area-title').innerText = areaNome;
            estadoAtual.area = areaNome;
        }

        // 1. Cria o grupo que vai conter o Título e as Abas
        const areaGroup = document.createElement('div');
        areaGroup.className = 'area-group';

        // 2. Título da Área agora é um botão clicável
        const areaTitle = document.createElement('div');
        areaTitle.className = 'area-title';
        areaTitle.innerHTML = `<span>${areaNome}</span> <i class="fa-solid fa-chevron-down toggle-icon"></i>`;

        // 3. Container das abas (inicia oculto)
        const tabsContainer = document.createElement('div');
        tabsContainer.className = 'area-tabs hidden';

        // 4. Lógica de Clique (Expandir/Retrair)
        areaTitle.onclick = () => {
            const isClosed = tabsContainer.classList.contains('hidden');
            
            // Fecha todos os outros grupos (Accordion exclusivo)
            document.querySelectorAll('.area-tabs').forEach(tab => tab.classList.add('hidden'));
            document.querySelectorAll('.area-title .toggle-icon').forEach(icon => {
                icon.classList.remove('fa-chevron-up');
                icon.classList.add('fa-chevron-down');
            });

            // Se o que foi clicado estava fechado, ele abre agora
            if (isClosed) {
                tabsContainer.classList.remove('hidden');
                areaTitle.querySelector('.toggle-icon').classList.replace('fa-chevron-down', 'fa-chevron-up');
            }
            
            // Atualiza o título do painel lateral
            document.getElementById('current-area-title').innerText = areaNome;
            estadoAtual.area = areaNome;
        };

        areaGroup.appendChild(areaTitle);
        areaGroup.appendChild(tabsContainer);
        container.appendChild(areaGroup);

        // 5. Busca as abas (funcionalidades) e anexa dentro do tabsContainer
        const abas = await eel.get_abas(estadoAtual.superarea, areaNome)();
        
        abas.forEach(abaNome => {
            const btn = document.createElement('button');
            btn.className = 'btn-side';
            let icone = 'fa-file-lines';
            if(abaNome.includes('Painel') || abaNome.includes('Radar')) icone = 'fa-chart-line';
            if(abaNome.includes('Batimento')) icone = 'fa-code-compare';
            
            btn.innerHTML = `<i class="fa-solid ${icone}"></i> ${abaNome}`;
            btn.onclick = () => selecionarAba(areaNome, abaNome, btn);
            tabsContainer.appendChild(btn);
        });
    }
}

async function selecionarAba(areaNome, abaNome, btnElement) {
    estadoAtual.area = areaNome;
    estadoAtual.aba = abaNome;

    document.querySelectorAll('.btn-side').forEach(b => b.classList.remove('active'));
    btnElement.classList.add('active');
    document.getElementById('current-area-title').innerText = areaNome;
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active-view'));

    const viewData = await eel.carregar_conteudo_aba(estadoAtual.superarea, areaNome, abaNome)();

    if (viewData.tipo === "batimento_om5") {
        document.getElementById('view-batimento').classList.add('active-view');
    } 
    else if (viewData.tipo === "formulario_ocorrencia") {
        document.getElementById('view-formulario').classList.add('active-view');
    } 
    else if (viewData.tipo === "painel_gestor") {
        document.getElementById('view-painel').classList.add('active-view');
        carregarPainel('abertas');
    }
    else {
        document.getElementById('dev-title').innerText = viewData.titulo;
        document.getElementById('dev-msg').innerText = viewData.mensagem;
        document.getElementById('view-dev').classList.add('active-view');
    }
}

function voltarInicio() {
    estadoAtual = { superarea: null, area: null, aba: null };
    
    document.querySelectorAll('.btn-top').forEach(b => b.classList.remove('active'));
    document.getElementById('current-superarea-badge').innerText = "Início";
    document.getElementById('current-area-title').innerText = "Menu Principal";
    document.getElementById('side-menu-container').innerHTML = '<div class="empty-state">Selecione um módulo no menu superior</div>';
    
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active-view'));
    document.getElementById('view-welcome').classList.add('active-view');
}

// ================= LOGS =================
async function atualizarLogs() {
    const logs = await eel.buscar_logs()();
    const container = document.getElementById('sys-logs');
    
    container.innerHTML = logs.map(msg => {
        const partes = msg.split('] ');
        if(partes.length === 2) {
            return `<div class="log-line"><span class="log-time">${partes[0]}]</span>${partes[1]}</div>`;
        }
        return `<div class="log-line">${msg}</div>`;
    }).join('');
    
    container.scrollTop = container.scrollHeight;
}

function toggleLogs() {
    const container = document.getElementById('terminal-container');
    const icon = document.getElementById('log-toggle-icon');
    
    container.classList.toggle('collapsed');
    
    if (container.classList.contains('collapsed')) {
        icon.classList.remove('fa-chevron-down');
        icon.classList.add('fa-chevron-up');
    } else {
        icon.classList.remove('fa-chevron-up');
        icon.classList.add('fa-chevron-down');
    }
}

// ================= FORMULÁRIO =================
function toggleExtra(id, show) {
    const el = document.getElementById(id);
    if (show) el.classList.remove('hidden');
    else el.classList.add('hidden');
}

async function enviarFormulario(e) {
    e.preventDefault();
    
    const dados = {
        data: document.getElementById('f_data').value,
        hora: document.getElementById('f_hora').value,
        area: document.getElementById('f_area').value,
        sistema: document.getElementById('f_sistema').value,
        descricao: document.getElementById('f_descricao').value,
        impacto: document.getElementById('f_impacto').value,
        
        descumprimento: document.querySelector('input[name="r_descumprimento"]:checked').value,
        desc_detalhe: document.getElementById('f_desc_detalhe').value,
        
        reincidencia: document.querySelector('input[name="r_reincidencia"]:checked').value,
        rein_data: document.getElementById('f_rein_data').value,
        
        risco: document.querySelector('input[name="r_risco"]:checked').value,
        risco_desc: document.getElementById('f_risco_desc').value,
        risco_valor: document.getElementById('f_risco_valor').value,
        
        impacto_cliente: document.querySelector('input[name="r_cliente"]:checked').value,
        imp_cliente_desc: document.getElementById('f_imp_cliente').value,
        
        plano_acao: document.querySelector('input[name="r_plano"]:checked').value,
        plano_desc: document.getElementById('f_plano_desc').value,
        resp_plano: document.getElementById('f_resp_plano').value,
        prazo: document.getElementById('f_prazo').value,
    };

    const result = await eel.salvar_nova_ocorrencia(dados)();
    if(result.status === "sucesso") {
        alert(`Ocorrência OC-${result.id.toString().padStart(3, '0')} registrada com sucesso!`);
        document.getElementById('form-ocorrencia').reset();
        ['extra_descumprimento', 'extra_reincidencia', 'extra_risco', 'extra_cliente', 'extra_plano'].forEach(id => toggleExtra(id, false));
    }
}

// ================= PAINEL E MODAL =================
function getStatusClass(status) {
    const map = {"Aberto": "st-aberto", "Em Análise": "st-analise", "Mitigado": "st-mitigado", "Fechado": "st-fechado"};
    return map[status] || "st-aberto";
}

async function carregarPainel(filtro) {
    document.querySelectorAll('.btn-tab').forEach(b => b.classList.remove('active'));
    if(filtro === 'abertas') {
        document.getElementById('tab-abertas').classList.add('active');
        document.getElementById('painel-title').innerText = "Ocorrências em Aberto";
    } else {
        document.getElementById('tab-historico').classList.add('active');
        document.getElementById('painel-title').innerText = "Histórico Completo";
    }

    const ocorrencias = await eel.get_lista_ocorrencias(filtro)();
    const tbody = document.getElementById('tabela-corpo');
    
    tbody.innerHTML = ocorrencias.map(o => `
        <tr>
            <td>OC-${o.id.toString().padStart(3, '0')}</td>
            <td>${o.data}</td>
            <td>${o.area}</td>
            <td>${o.sistema}</td>
            <td><span class="status-badge ${getStatusClass(o.status)}">${o.status}</span></td>
            <td><button class="btn-acao" onclick="abrirModal(${o.id})">Detalhes</button></td>
        </tr>
    `).join('');
}

async function abrirModal(id) {
    const res = await eel.get_detalhes_ocorrencia(id)();
    const d = res.dados;
    
    document.getElementById('mod-title').innerText = `Registro Operacional: OC-${d.id.toString().padStart(3, '0')}`;
    
    let html = `
        <div class="mod-section">
            <div class="mod-sec-title">Atualizar Status e Progresso</div>
            <div style="display: flex; gap: 12px; align-items: center;">
                <select id="select-status-${d.id}" class="form-control" style="max-width: 200px;">
                    <option value="Aberto" ${d.status === 'Aberto' ? 'selected' : ''}>Aberto</option>
                    <option value="Em Análise" ${d.status === 'Em Análise' ? 'selected' : ''}>Em Análise</option>
                    <option value="Mitigado" ${d.status === 'Mitigado' ? 'selected' : ''}>Mitigado</option>
                    <option value="Fechado" ${d.status === 'Fechado' ? 'selected' : ''}>Fechado</option>
                </select>
                <button class="btn-primary" style="padding: 8px 16px;" onclick="atualizarStatusOcorrencia(${d.id})">Gravar Atualização</button>
            </div>
        </div>

        <div class="mod-section">
            <div class="mod-sec-title">Informações Básicas</div>
            <div class="mod-row"><span class="mod-lbl">Status Atual:</span><span class="status-badge ${getStatusClass(d.status)}">${d.status}</span></div>
            <div class="mod-row"><span class="mod-lbl">Data/Hora:</span><span class="mod-val">${d.data} às ${d.hora}</span></div>
            <div class="mod-row"><span class="mod-lbl">Área/Coordenação:</span><span class="mod-val">${d.area}</span></div>
            <div class="mod-row"><span class="mod-lbl">Sistema:</span><span class="mod-val">${d.sistema}</span></div>
        </div>

        <div class="mod-section">
            <div class="mod-sec-title">Detalhes do Incidente</div>
            <div class="mod-row"><span class="mod-lbl">Descrição:</span></div>
            <div class="mod-val-long mb-2">${d.descricao}</div>
            <div class="mod-row"><span class="mod-lbl">Impacto Gerado:</span></div>
            <div class="mod-val-long">${d.impacto}</div>
        </div>
        
        <div class="mod-section">
            <div class="mod-sec-title">Análise e Procedimentos</div>
            <div class="mod-row"><span class="mod-lbl">Descumprimento?</span><span class="mod-val">${d.descumprimento}</span></div>
            ${d.descumprimento === 'Sim' ? `<div class="mod-row"><span class="mod-lbl">↳ Detalhe:</span><span class="mod-val">${d.desc_detalhe}</span></div>` : ''}
            
            <div class="mod-row" style="margin-top:10px;"><span class="mod-lbl">Reincidência?</span><span class="mod-val">${d.reincidencia}</span></div>
            ${d.reincidencia === 'Sim' ? `<div class="mod-row"><span class="mod-lbl">↳ Data Anterior:</span><span class="mod-val">${d.rein_data}</span></div>` : ''}
            
            <div class="mod-row" style="margin-top:10px;"><span class="mod-lbl">Risco ou Perda?</span><span class="mod-val">${d.risco}</span></div>
            ${d.risco === 'Sim' ? `<div class="mod-row"><span class="mod-lbl">↳ Descrição:</span><span class="mod-val">${d.risco_desc}</span></div>
                                   <div class="mod-row"><span class="mod-lbl">↳ Valor:</span><span class="mod-val">${d.risco_valor}</span></div>` : ''}
                                   
            <div class="mod-row" style="margin-top:10px;"><span class="mod-lbl">Plano de Ação?</span><span class="mod-val">${d.plano_acao || 'Não'}</span></div>
            ${d.plano_acao === 'Sim' ? `<div class="mod-row"><span class="mod-lbl">↳ Descrição:</span><span class="mod-val">${d.plano_desc}</span></div>
                                        <div class="mod-row"><span class="mod-lbl">↳ Responsável:</span><span class="mod-val">${d.resp_plano}</span></div>
                                        <div class="mod-row"><span class="mod-lbl">↳ Prazo:</span><span class="mod-val">${d.prazo}</span></div>` : ''}
        </div>
        
        <div class="mod-section">
            <div class="mod-sec-title">Histórico de Status</div>
            ${res.historico ? res.historico.map(h => `
                <div class="hist-item">
                    <div class="hist-head"><span>${h.data_hora}</span><span class="status-badge ${getStatusClass(h.status_novo)}">${h.status_novo}</span></div>
                    <div>${h.comentario}</div>
                </div>
            `).join('') : '<div class="mod-val-long">Sem histórico registrado.</div>'}
        </div>
    `;

    document.getElementById('mod-body').innerHTML = html;
    document.getElementById('modal-backdrop').classList.remove('hidden');
}

function fecharModal() {
    document.getElementById('modal-backdrop').classList.add('hidden');
}

async function atualizarStatusOcorrencia(id) {
    const novoStatus = document.getElementById(`select-status-${id}`).value;
    
    try {
        await eel.atualizar_status_ocorrencia(id, novoStatus)();
        alert(`Status da ocorrência OC-${id.toString().padStart(3, '0')} foi atualizado com sucesso para "${novoStatus}".`);
    } catch (error) {
        console.warn("A função eel.atualizar_status_ocorrencia não foi encontrada no Python.");
        alert(`[SIMULAÇÃO] A ocorrência foi atualizada para "${novoStatus}".\nPara funcionar no banco de dados real, implemente a função 'atualizar_status_ocorrencia(id, status)' no app.py.`);
    }

    fecharModal();
    const isAbertas = document.getElementById('tab-abertas').classList.contains('active');
    carregarPainel(isAbertas ? 'abertas' : 'todas');
}