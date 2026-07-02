import eel
import os
import time
import config
from logger import sistema_logger
from db_mock import db  # Adicionado para a mockagem de dados
#from database import db

# =================================================================
# ESTRUTURA DE DADOS (Substitui o self.SUPERAREAS do Tkinter)
# =================================================================
SUPERAREAS = {
    'Financeiro': {
        'Escrituração': ['Cadastro de Evento', 'Radar de Contas', 'Anexos OM5', 'Checklist', 
                        'Painel de acompanhamento', 'Salvar Extratos', 'Batimento de Provisão', 
                        'Radar de Eventos', 'Batimento OM5'],
        'Financeiro B3': ['Checklist', 'Painel de Acompanhamento', 'Envio de Taxas', 
                         'Radar de Eventos', 'Radar de Saldos', 'Relação de Contas', 
                         'BTB', 'STR', 'E-mails corretoras'],
        'Câmbio e Caixa': ['Checklist', 'Painel de Acompanhamento', 'Vendas Descobertas'],
        'Painel de Eventos': ['Painel de Eventos'],
        'Copiloto': ['Processo 1', 'Processo 2']
    },
    'RV': {
        'Esteira 1': ['Processo 1', 'Processo 2'],
        'Esteira 2': ['Processo 1', 'Processo 2']
    },
    'RF': {
        'CETIP': ['Checklist', 'Painel de Acompanhamento'],
        'Esteira 2': ['Processo 1', 'Processo 2']
    },
    'Ocorrências': {
        'Relatório de Ocorrências': ['Formulário', 'Painel']
    }
}

# =================================================================
# FUNÇÕES EXPOSTAS PARA O FRONT-END HTML (API)
# =================================================================
@eel.expose
def get_config_iniciais():
    """Retorna configurações iniciais para popular a interface"""
    return {
        "titulo": config.NOME_JANELA,
        "data_atual": f"{config.DIA} de {config.MES_NOME} de {config.ANO}",
        "superareas": list(SUPERAREAS.keys())
    }

@eel.expose
def get_areas(superarea):
    """Retorna as áreas de uma superárea específica"""
    if superarea in SUPERAREAS:
        return list(SUPERAREAS[superarea].keys())
    return []

@eel.expose
def get_abas(superarea, area):
    """Retorna as abas (funcionalidades) de uma área específica"""
    try:
        return SUPERAREAS[superarea][area]
    except KeyError:
        return []

@eel.expose
def carregar_conteudo_aba(superarea, area, aba):
    """
    Simula a inicialização das Views do código antigo (WelcomeView, RelacaoContasView, etc).
    Retorna os dados necessários para o JavaScript desenhar a tela correspondente.
    """
    sistema_logger.log(f"Usuário acessou: {superarea} > {area} > {aba}")
    
    # Roteamento baseado na aba selecionada
    if aba == "Batimento OM5":
        return {
            "tipo": "batimento_om5",
            "titulo": "Batimento OM5 - Conciliação",
            "status": "operacional"
        }
    elif aba == "Formulário":
        return {
            "tipo": "formulario_ocorrencia",
            "titulo": "Registro de Ocorrências Internas",
            "status": "operacional"
        }
    elif aba == "Painel":
        return {
            "tipo": "painel_gestor",
            "titulo": "Painel do Gestor",
            "status": "operacional"
        }
    else:
        return {
            "tipo": "desenvolvimento",
            "titulo": f"{aba}",
            "mensagem": "Esta tela ainda está sendo portada para o novo sistema web."
        }

@eel.expose
def buscar_logs():
    return sistema_logger.obter_logs_recentes(15)

# =================================================================
# ENDPOINTS DO BANCO DE DADOS (OCORRÊNCIAS)
# =================================================================
@eel.expose
def get_lista_ocorrencias(filtro="abertas"):
    sistema_logger.log(f"Buscando ocorrências: {filtro}")
    if filtro == "abertas":
        return db.obter_ativas()
    else:
        return db.obter_todas()

@eel.expose
def get_detalhes_ocorrencia(id_ocorrencia):
    sistema_logger.log(f"Consultando detalhes da OC-{id_ocorrencia}")
    return {
        "dados": db.obter_por_id(id_ocorrencia),
        "historico": db.obter_historico(id_ocorrencia)
    }

@eel.expose
def salvar_nova_ocorrencia(dados_form):
    sistema_logger.log(f"Salvando nova ocorrência do sistema: {dados_form.get('sistema')}")
    novo_id = db.inserir_nova(dados_form)
    return {"status": "sucesso", "id": novo_id}

@eel.expose
def atualizar_status_ocorrencia(id_ocorrencia, novo_status):
    db.atualizar_status(id_ocorrencia, novo_status) # Sua lógica interna
    return {"status": "sucesso"}


# =================================================================
# INICIALIZAÇÃO DO SERVIDOR LOCAL
# =================================================================
if __name__ == '__main__':
    print(f"[{config.NOME_JANELA}] Inicializando motor web...")
    sistema_logger.log("Sistema iniciado.")
    
    # Inicia o Eel
    eel.init('web')
    
    # Inicia como App Desktop nativo. 
    # Para virar Intranet, bastaria trocar para: eel.start('index.html', mode=None, host='0.0.0.0', port=8000)
    eel.start('index.html', size=(1280, 800), mode='chrome')


# pyinstaller --noconfirm --onefile --windowed --add-data "web;web" --exclude-module PyQt5 --exclude-module PyQt6 --hidden-import holidays.countries app.py