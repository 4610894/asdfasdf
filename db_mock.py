class BancoDeDadosMock:
    def __init__(self):
        self.ocorrencias = [
            {
                "id": 1, "data": "20/06/2026", "hora": "14:30", "area": "Operações TI", "sistema": "Servidor Principal", 
                "descricao": "Queda do servidor devido a falha elétrica na fase 2 do data center.", 
                "impacto": "Parada total do sistema de vendas por 2h.", "status": "Aberto",
                "descumprimento": "Sim", "desc_detalhe": "O gerador de backup não foi testado na última janela.",
                "plano_acao": "Sim", 
                "reincidencia": "Não", "rein_data": "",
                "risco": "Sim", "risco_desc": "Perda de transações financeiras durante a queda.", "risco_valor": "R$ 45.000,00",
                "impacto_cliente": "Sim", "imp_cliente_desc": "Clientes não conseguiram finalizar compras no app.",
                "resp_plano": "Carlos Silva", "prazo": "25/06/2026"
            },
            {
                "id": 2, "data": "21/06/2026", "hora": "09:15", "area": "Atendimento", "sistema": "CRM", 
                "descricao": "Lentidão ao buscar cadastro de clientes antigos.", 
                "impacto": "Aumento no tempo de espera do call center.", "status": "Em Análise",
                "descumprimento": "Não", "desc_detalhe": "",
                "plano_acao": "Sim", 
                "reincidencia": "Sim", "rein_data": "10/05/2026",
                "risco": "Não", "risco_desc": "", "risco_valor": "",
                "impacto_cliente": "Sim", "imp_cliente_desc": "Maior tempo de espera nas ligações (TMA alto).",
                "resp_plano": "Ana Souza", "prazo": "30/06/2026"
            },
            {
                "id": 3, "data": "22/06/2026", "hora": "18:45", "area": "Logística", "sistema": "Roteirizador", 
                "descricao": "Erro na API de integração com mapas.", 
                "impacto": "Atraso na montagem de rotas de entrega diárias.", "status": "Mitigado",
                "descumprimento": "Não", "desc_detalhe": "",
                "plano_acao": "Não", 
                "reincidencia": "Não", "rein_data": "",
                "risco": "Não", "risco_desc": "", "risco_valor": "",
                "impacto_cliente": "Não", "imp_cliente_desc": "",
                "resp_plano": "Pendente", "prazo": "Pendente"
            }
        ]

        self.historico = {
            1: [{"data_hora": "20/06/2026 15:00", "status_novo": "Aberto", "comentario": "Ocorrência registrada."}],
            2: [
                {"data_hora": "21/06/2026 10:00", "status_novo": "Aberto", "comentario": "Ocorrência registrada."},
                {"data_hora": "21/06/2026 14:00", "status_novo": "Em Análise", "comentario": "Equipe de banco de dados acionada."}
            ],
            3: [
                {"data_hora": "22/06/2026 19:00", "status_novo": "Aberto", "comentario": "Registrado."},
                {"data_hora": "22/06/2026 19:30", "status_novo": "Mitigado", "comentario": "Trocado para provedor de mapa secundário."}
            ]
        }

    def obter_ativas(self):
        return [o for o in self.ocorrencias if o["status"] != "Fechado"]

    def obter_todas(self):
        return self.ocorrencias

    def obter_por_id(self, id_ocorrencia):
        for o in self.ocorrencias:
            if o["id"] == id_ocorrencia:
                return o
        return None

    def obter_historico(self, id_ocorrencia):
        return self.historico.get(id_ocorrencia, [])
        
    def inserir_nova(self, dados):
        novo_id = max([o["id"] for o in self.ocorrencias]) + 1 if self.ocorrencias else 1
        dados["id"] = novo_id
        dados["status"] = "Aberto"
        self.ocorrencias.append(dados)
        
        import datetime
        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        self.historico[novo_id] = [{"data_hora": agora, "status_novo": "Aberto", "comentario": "Ocorrência registrada via Formulário Web."}]
        return novo_id

db = BancoDeDadosMock()
