# 1. Alterações no Banco de Dados (database.py)
# Adicione estes novos métodos dentro da sua classe DatabaseManager já existente. Eles executam exatamente as mesmas queries do seu código Tkinter original.

# Onde inserir: No final do arquivo database.py, dentro da classe DatabaseManager, logo acima da linha db = DatabaseManager().

# ================= FUNCIONALIDADES: CHECKLIST CETIP =================
    def ch_inicializar_dia(self):
        """Insere as tarefas diárias e atualiza atrasos (Substitui inserir_dados e revisar_status)"""
        if not self.conn: return
        hoje = datetime.date.today().strftime("%Y-%m-%d")
        
        # 1. Verifica e insere tarefas do dia
        self.cursor.execute("SELECT TOP 1 data FROM liq.CHECKLIST_EXECUCAO WHERE data = ?", (hoje,))
        if not self.cursor.fetchone():
            self.cursor.execute("SELECT id FROM liq.CHECKLIST_TAREFAS WHERE esteira NOT LIKE 'ES - %'")
            tarefas = self.cursor.fetchall()
            for t in tarefas:
                self.cursor.execute("INSERT INTO liq.CHECKLIST_EXECUCAO (id_tarefa, data, status) VALUES (?, ?, 'Pendente')", (t[0], hoje))
        
        # 2. Revisa status para "Em atraso"
        query_atraso = """
            UPDATE liq.CHECKLIST_EXECUCAO
            SET status = 'Em atraso'
            FROM liq.CHECKLIST_EXECUCAO e
            JOIN liq.CHECKLIST_TAREFAS t ON e.id_tarefa = t.id
            WHERE e.status = 'Pendente' 
            AND e.data = CONVERT(date, GETDATE())
            AND GETDATE() > CAST(e.data AS DATETIME) + CAST(t.horario_conclusao AS DATETIME)
        """
        self.cursor.execute(query_atraso)
        self.conn.commit()

    def ch_consultar(self, data, status, tarefa, esteira):
        if not self.conn: return []
        query = """
            SELECT t.id AS id_tarefa, t.tarefa, t.esteira, t.data AS data_evento, e.status, 
                   e.responsavel, e.observacoes, e.data_atualizacao
            FROM liq.CHECKLIST_EXECUCAO e
            JOIN liq.CHECKLIST_TAREFAS t ON e.id_tarefa = t.id
            WHERE 1=1
        """
        params = []
        if data:
            query += " AND e.data = ?"; params.append(data)
        if status and status != "Todos":
            query += " AND e.status = ?"; params.append(status)
        if tarefa:
            query += " AND t.tarefa LIKE ?"; params.append(f"%{tarefa}%")
        if esteira and esteira != "Todas":
            if esteira == "Pendente": # Lógica original do Tkinter para esteira 'Pendente'
                query += " AND t.esteira LIKE 'ES - %'"
            else:
                query += " AND t.esteira = ?"; params.append(esteira)
                
        query += " ORDER BY t.horario_conclusao"
        self.cursor.execute(query, params)
        return [self._formatar_linha(row, self.cursor) for row in self.cursor.fetchall()]

    def ch_atualizar_celula(self, id_tarefa, data_evento, coluna, novo_valor):
        if not self.conn: return False
        try:
            # Proteção contra SQL Injection mapeando a coluna permitida
            colunas_validas = {"status": "status", "responsavel": "responsavel", "observacoes": "observacoes"}
            col_db = colunas_validas.get(coluna)
            if not col_db: return False

            query = f"""
                UPDATE liq.CHECKLIST_EXECUCAO
                SET {col_db} = ?, data_atualizacao = SYSDATETIME()
                WHERE id_tarefa = ? AND data = ?
            """
            self.cursor.execute(query, (novo_valor, id_tarefa, data_evento))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar célula: {e}")
            return False

    def ch_eventos_especiais(self, acao, tarefa=None, esteira=None):
        if not self.conn: return []
        hoje = datetime.date.today().strftime("%Y-%m-%d")
        
        if acao == "listar":
            self.cursor.execute("SELECT DISTINCT(tarefa) FROM liq.CHECKLIST_TAREFAS WHERE esteira LIKE 'ES - %'")
            return [row[0] for row in self.cursor.fetchall()]
            
        elif acao == "adicionar" or acao == "remover":
            self.cursor.execute("SELECT id FROM liq.CHECKLIST_TAREFAS WHERE tarefa = ? AND esteira LIKE 'ES - %'", (tarefa,))
            row = self.cursor.fetchone()
            if not row: return {"status": "erro", "msg": "Tarefa não encontrada."}
            id_tarefa = row[0]

            if acao == "adicionar":
                self.cursor.execute("SELECT 1 FROM liq.CHECKLIST_EXECUCAO WHERE id_tarefa = ? AND data = ?", (id_tarefa, hoje))
                if self.cursor.fetchone(): return {"status": "erro", "msg": "Evento já inserido hoje."}
                
                self.cursor.execute("INSERT INTO liq.CHECKLIST_EXECUCAO (id_tarefa, data, status, esteira) VALUES (?, ?, 'Pendente', ?)", (id_tarefa, hoje, esteira))
                self.conn.commit()
                return {"status": "sucesso", "msg": "Evento adicionado!"}
                
            elif acao == "remover":
                self.cursor.execute("DELETE FROM liq.CHECKLIST_EXECUCAO WHERE id_tarefa = ? AND data = ? AND esteira = ?", (id_tarefa, hoje, esteira))
                if self.cursor.rowcount > 0:
                    self.conn.commit()
                    return {"status": "sucesso", "msg": "Evento removido!"}
                return {"status": "erro", "msg": "Nenhum evento correspondente encontrado hoje."}





















# 1. Banco de Dados (database.py)
# Adicione estes dois novos métodos no final da classe DatabaseManager (logo abaixo dos que criamos na etapa anterior):

def ch_listar_tarefas_config(self):
        """Busca todas as tarefas cadastradas no banco para o painel de gerenciamento"""
        if not self.conn: return []
        self.cursor.execute("SELECT id, tarefa, horario_conclusao, esteira FROM liq.CHECKLIST_TAREFAS ORDER BY esteira, horario_conclusao")
        return [self._formatar_linha(row, self.cursor) for row in self.cursor.fetchall()]

    def ch_gerenciar_tarefa(self, acao, id_tarefa=None, tarefa=None, horario=None, esteira=None):
        """Realiza o CRUD (Inserir, Editar, Deletar) das tarefas"""
        if not self.conn: return False
        try:
            if acao == "adicionar":
                self.cursor.execute("INSERT INTO liq.CHECKLIST_TAREFAS (tarefa, horario_conclusao, esteira) VALUES (?, ?, ?)", (tarefa, horario, esteira))
            
            elif acao == "editar":
                self.cursor.execute("UPDATE liq.CHECKLIST_TAREFAS SET tarefa = ?, horario_conclusao = ?, esteira = ? WHERE id = ?", (tarefa, horario, esteira, id_tarefa))
            
            elif acao == "deletar":
                # É obrigatório deletar as execuções filhas primeiro para não dar erro de Chave Estrangeira
                self.cursor.execute("DELETE FROM liq.CHECKLIST_EXECUCAO WHERE id_tarefa = ?", (id_tarefa,))
                self.cursor.execute("DELETE FROM liq.CHECKLIST_TAREFAS WHERE id = ?", (id_tarefa,))
                
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao gerenciar tarefa: {e}")
            return False
