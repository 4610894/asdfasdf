// 4. Lógica JavaScript (main.js)Precisamos rotear a exibição e implementar a lógica de edição inline (duplo clique na tabela para editar), igual existia no Tkinter.A) Na função selecionarAba(areaNome, abaNome, btnElement):
// Adicione a nova condição de roteamento:  

else if (viewData.tipo === "checklist_rf") {
        document.getElementById('view-checklist').classList.add('active-view');
        ChecklistApp.iniciar();
    }


// B) No final do arquivo main.js:
// Adicione o namespace que controla o processo do Checklist:

// ================= MÓDULO CHECKLIST CETIP =================
const ChecklistApp = {
    abaAtiva: 'Todas',
    
    iniciar: async function() {
        // Inicializa tarefas do dia e status de atraso no backend
        await eel.checklist_init()();
        
        // Seta a data de hoje no input type="date"
        document.getElementById('ch_data').value = new Date().toISOString().split('T')[0];
        
        this.renderizarAbas();
        this.filtrar();
    },

    renderizarAbas: function() {
        const abas = ["Todas", "Pendente", "Em andamento", "Concluído", "Em atraso", "Não se aplica"];
        const container = document.getElementById('ch_abas');
        container.innerHTML = abas.map(aba => `
            <button class="btn-tab ${this.abaAtiva === aba ? 'active' : ''}" 
                    onclick="ChecklistApp.mudarAba('${aba}')">${aba}</button>
        `).join('');
        
        // Esconde a coluna 'Esteira' se não for a aba "Todas" (mesma regra do Tkinter)
        document.getElementById('th_esteira').style.display = (this.abaAtiva === 'Todas') ? '' : 'none';
    },

    mudarAba: function(novaAba) {
        this.abaAtiva = novaAba;
        this.renderizarAbas();
        this.filtrar();
    },

    filtrar: async function() {
        const filtros = {
            data: document.getElementById('ch_data').value,
            status: document.getElementById('ch_status').value,
            tarefa: document.getElementById('ch_tarefa').value,
            esteira: this.abaAtiva
        };

        const dados = await eel.checklist_consultar(filtros)();
        const tbody = document.getElementById('ch_tabela_corpo');
        
        tbody.innerHTML = dados.map(d => `
            <tr data-id="${d.id_tarefa}" data-evento="${d.data_evento}">
                <td style="display:none;">${d.id_tarefa}</td>
                <td>${d.tarefa}</td>
                <td>${d.data_evento || ''}</td>
                <td ondblclick="ChecklistApp.editarCelula(this, 'status', '${d.status}')"><span class="status-badge ${getStatusClass(d.status)}">${d.status}</span></td>
                <td ondblclick="ChecklistApp.editarCelula(this, 'responsavel', '${d.responsavel}')">${d.responsavel || '---'}</td>
                <td ondblclick="ChecklistApp.editarCelula(this, 'observacoes', '${d.observacoes}')">${d.observacoes || '---'}</td>
                <td>${d.data_atualizacao || ''}</td>
                <td style="display: ${this.abaAtiva === 'Todas' ? '' : 'none'};">${d.esteira || ''}</td>
            </tr>
        `).join('');
    },

    editarCelula: function(td, coluna, valorAtual) {
        // Evita abrir duplo editor
        if(td.querySelector('input') || td.querySelector('select')) return;
        
        const isStatus = coluna === 'status';
        let editorHTML = '';

        if(isStatus) {
            const opcoes = ["", "Pendente", "Em andamento", "Concluído", "Não se aplica"];
            editorHTML = `<select class="form-control" style="padding: 2px; height: 30px;" onblur="ChecklistApp.salvarCelula(this, '${coluna}', '${valorAtual}')">
                ${opcoes.map(o => `<option value="${o}" ${o === valorAtual ? 'selected' : ''}>${o}</option>`).join('')}
            </select>`;
        } else {
            // Corrige exibição de '---' no input
            const val = valorAtual === '---' || valorAtual === 'null' ? '' : valorAtual;
            editorHTML = `<input type="text" class="form-control" style="padding: 2px; height: 30px;" value="${val}" 
                onblur="ChecklistApp.salvarCelula(this, '${coluna}', '${valorAtual}')"
                onkeydown="if(event.key === 'Enter') this.blur();">`;
        }
        
        td.innerHTML = editorHTML;
        td.firstElementChild.focus();
    },

    salvarCelula: async function(elemento, coluna, valorAntigo) {
        const td = elemento.parentElement;
        const tr = td.parentElement;
        const novoValor = elemento.value;
        const id_tarefa = tr.getAttribute('data-id');
        const data_evento = tr.getAttribute('data-evento');

        if(novoValor !== valorAntigo) {
            const sucesso = await eel.checklist_atualizar_celula(parseInt(id_tarefa), data_evento, coluna, novoValor)();
            if(sucesso) {
                this.filtrar(); // Recarrega a tabela para trazer a Data de Atualização nova
                return;
            }
        }
        
        // Se não mudou ou deu erro, restaura o visual antigo
        if(coluna === 'status') {
            td.innerHTML = `<span class="status-badge ${getStatusClass(valorAntigo)}">${valorAntigo}</span>`;
        } else {
            td.innerHTML = valorAntigo || '---';
        }
    },

    abrirModalEvento: async function() {
        const tarefas = await eel.checklist_gerenciar_evento('listar')();
        const select = document.getElementById('ch_modal_tarefa');
        select.innerHTML = tarefas.map(t => `<option value="${t}">${t}</option>`).join('');
        document.getElementById('modal-evento-especial').classList.remove('hidden');
    },

    gerenciarEvento: async function(acao) {
        const tarefa = document.getElementById('ch_modal_tarefa').value;
        const esteira = document.getElementById('ch_modal_esteira').value;
        
        const res = await eel.checklist_gerenciar_evento(acao, tarefa, esteira)();
        alert(res.msg);
        
        if(res.status === 'sucesso') {
            document.getElementById('modal-evento-especial').classList.add('hidden');
            this.filtrar();
        }
    }
};























// 4. Lógica JavaScript (main.js)
// Cole todas estas novas funções dentro do objeto ChecklistApp (por exemplo, logo após a função gerenciarEvento: async function(...) { ... }). Lembre-se de colocar uma vírgula , após a função anterior para separar.


// ================= FUNCIONALIDADES: GERENCIAR TAREFAS =================
    
    abrirModalGerenciarTarefas: async function() {
        document.getElementById('modal-gerenciar-tarefas').classList.remove('hidden');
        this.cancelarEdicaoTarefa(); // Limpa o formulário caso tivesse algo preenchido
        await this.carregarListaTarefas();
    },

    carregarListaTarefas: async function() {
        const tarefas = await eel.checklist_listar_tarefas()();
        const tbody = document.getElementById('gt_tabela_corpo');
        
        tbody.innerHTML = tarefas.map(t => {
            // Garante que o horário vai ser exibido como HH:MM
            const horarioFormatado = t.horario_conclusao ? t.horario_conclusao.substring(0, 5) : '';
            // Protege aspas simples para não quebrar o clique do botão HTML
            const tarefaLimpa = t.tarefa ? t.tarefa.replace(/'/g, "\\'") : '';
            
            return `
            <tr>
                <td>${t.tarefa}</td>
                <td>${horarioFormatado}</td>
                <td>${t.esteira}</td>
                <td style="text-align: center;">
                    <button class="btn-acao" title="Editar" onclick="ChecklistApp.prepararEdicaoTarefa(${t.id}, '${tarefaLimpa}', '${horarioFormatado}', '${t.esteira}')"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-acao" title="Excluir" style="background-color: #d9534f;" onclick="ChecklistApp.deletarTarefa(${t.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            </tr>`;
        }).join('');
    },

    prepararEdicaoTarefa: function(id, tarefa, horario, esteira) {
        document.getElementById('lbl_titulo_form_tarefa').innerText = "Editar Tarefa Selecionada";
        document.getElementById('gt_id_tarefa').value = id;
        document.getElementById('gt_tarefa').value = tarefa;
        document.getElementById('gt_horario').value = horario; 
        document.getElementById('gt_esteira').value = esteira;
        
        document.getElementById('btn_salvar_tarefa').innerText = "Salvar Alterações";
        document.getElementById('btn_cancelar_edicao').classList.remove('hidden');
    },

    cancelarEdicaoTarefa: function() {
        document.getElementById('lbl_titulo_form_tarefa').innerText = "Adicionar Nova Tarefa";
        document.getElementById('gt_id_tarefa').value = '';
        document.getElementById('gt_tarefa').value = '';
        document.getElementById('gt_horario').value = '';
        document.getElementById('gt_esteira').value = '';
        
        document.getElementById('btn_salvar_tarefa').innerText = "Adicionar Tarefa";
        document.getElementById('btn_cancelar_edicao').classList.add('hidden');
    },

    salvarTarefa: async function() {
        const id = document.getElementById('gt_id_tarefa').value;
        const tarefa = document.getElementById('gt_tarefa').value;
        const horario = document.getElementById('gt_horario').value;
        const esteira = document.getElementById('gt_esteira').value;

        if(!tarefa || !horario || !esteira) {
            alert("Por favor, preencha o Nome, Horário e a Esteira da tarefa.");
            return;
        }

        const acao = id ? "editar" : "adicionar";
        const idInt = id ? parseInt(id) : null;

        const sucesso = await eel.checklist_crud_tarefa(acao, idInt, tarefa, horario, esteira)();
        if(sucesso) {
            this.cancelarEdicaoTarefa();
            await this.carregarListaTarefas();
            this.filtrar(); // Atualiza a tabela principal atrás do modal
        } else {
            alert("Erro ao salvar tarefa no banco de dados.");
        }
    },

    deletarTarefa: async function(id) {
        if(confirm("ATENÇÃO: Tem certeza que deseja excluir esta tarefa permanentemente?\n\nTodas as execuções antigas dela também serão apagadas.")) {
            const sucesso = await eel.checklist_crud_tarefa("deletar", parseInt(id))();
            if(sucesso) {
                await this.carregarListaTarefas();
                this.filtrar(); // Atualiza a tabela principal atrás do modal
            } else {
                alert("Erro ao excluir tarefa.");
            }
        }
    }






















// 2. Roteamento JavaScript (main.js)No arquivo main.js, vá até a função selecionarAba e atualize a condição do Checklist para capturar essa lista que o Python enviou e passá-la para o módulo.  Como deve ficar:


    else if (viewData.tipo === "checklist_rf") {
        document.getElementById('view-checklist').classList.add('active-view');
        // Agora passamos a lista injetada pelo app.py direto para a inicialização
        ChecklistApp.iniciar(viewData.esteiras); 
    }















// 3. Módulo Checklist (main.js)
// Ainda no main.js, localize o objeto ChecklistApp que criamos na resposta anterior. Vamos atualizá-lo para parar de usar aquela lista "chumbada" (hardcoded) e usar a lista dinâmica que chegou.

// Como deve ficar a parte superior do objeto:

const ChecklistApp = {
    abaAtiva: 'Todas',
    esteirasAtuais: [], // Nova variável para guardar as esteiras injetadas
    
    iniciar: async function(esteiras) {
        // Recebe as esteiras da configuração e salva na memória local
        this.esteirasAtuais = esteiras || ["Todas"]; 
        
        // Se a aba ativa não estiver na nova lista (ex: usuário trocou de menu), reseta
        if (!this.esteirasAtuais.includes(this.abaAtiva)) {
            this.abaAtiva = 'Todas';
        }

        await eel.checklist_init()();
        document.getElementById('ch_data').value = new Date().toISOString().split('T')[0];
        
        this.renderizarAbas();
        this.filtrar();
    },

    renderizarAbas: function() {
        const container = document.getElementById('ch_abas');
        // Agora ele desenha os botões baseado na configuração do Python
        container.innerHTML = this.esteirasAtuais.map(aba => `
            <button class="btn-tab ${this.abaAtiva === aba ? 'active' : ''}" 
                    onclick="ChecklistApp.mudarAba('${aba}')">${aba}</button>
        `).join('');
        
        document.getElementById('th_esteira').style.display = (this.abaAtiva === 'Todas') ? '' : 'none';
    },

    // ... o restante das funções (mudarAba, filtrar, etc) continua idêntico!
