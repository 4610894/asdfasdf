import pyodbc
import datetime
import config

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            # Mantive a sua string de conexão original
            self.conn = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                f'SERVER={config.SERVER};'
                f'DATABASE={config.DATABASE};'
                f'UID={config.USERNAME};'
                f'PWD={config.PASSWORD}'
            )
            self.cursor = self.conn.cursor()
            print('Conexão com o banco de dados estabelecida.')
        except pyodbc.Error as e:
            # Dica: Evite usar 'messagebox' (Tkinter) aqui, pois estamos em um sistema Web/Eel agora.
            print(f"ERRO CRÍTICO - Não foi possível conectar ao banco:\n{e}")
            self.conn = None
            self.cursor = None

    def _formatar_linha(self, row, cursor):
        """Transforma a linha crua do SQL em um Dicionário para o JS entender"""
        columns = [column[0] for column in cursor.description]
        row_dict = dict(zip(columns, row))
        
        # Converte formatos de data do banco para strings legíveis pelo Eel/JS
        for key, value in row_dict.items():
            if value is None:
                row_dict[key] = ""
            elif isinstance(value, datetime.datetime):
                row_dict[key] = value.strftime("%d/%m/%Y %H:%M")
            elif isinstance(value, datetime.date):
                row_dict[key] = value.strftime("%Y-%m-%d") # Padrão para input type="date"
            elif isinstance(value, datetime.time):
                # Pega apenas HORA:MINUTO (remove os segundos da string)
                row_dict[key] = value.strftime("%H:%M")
                
        return row_dict

    def obter_ativas(self):
        if not self.conn: return []
        self.cursor.execute("SELECT * FROM Ocorrencias WHERE status != 'Fechado' ORDER BY id DESC")
        return [self._formatar_linha(row, self.cursor) for row in self.cursor.fetchall()]

    def obter_todas(self):
        if not self.conn: return []
        self.cursor.execute("SELECT * FROM Ocorrencias ORDER BY id DESC")
        return [self._formatar_linha(row, self.cursor) for row in self.cursor.fetchall()]

    def obter_por_id(self, id_ocorrencia):
        if not self.conn: return None
        self.cursor.execute("SELECT * FROM Ocorrencias WHERE id = ?", (id_ocorrencia,))
        row = self.cursor.fetchone()
        return self._formatar_linha(row, self.cursor) if row else None

    def obter_historico(self, id_ocorrencia):
        if not self.conn: return []
        self.cursor.execute("SELECT data_hora, status_novo, comentario FROM Historico_Ocorrencias WHERE ocorrencia_id = ? ORDER BY data_hora DESC", (id_ocorrencia,))
        return [self._formatar_linha(row, self.cursor) for row in self.cursor.fetchall()]

    def inserir_nova(self, dados):
        if not self.conn: return -1
        
        query = """
            INSERT INTO Ocorrencias (
                data, hora, area, sistema, descricao, impacto, status, descumprimento,
                desc_detalhe, plano_acao, reincidencia, rein_data, risco, risco_desc,
                risco_valor, impacto_cliente, imp_cliente_desc, resp_plano, prazo
            ) VALUES (?, ?, ?, ?, ?, ?, 'Aberto', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # O input do tipo "date" em HTML devolve string vazia se não preenchido. 
        # O SQL Server espera NULL. Vamos tratar isso:
        rein_data = dados.get('rein_data') if dados.get('rein_data') else None
        prazo = dados.get('prazo') if dados.get('prazo') else None

        valores = (
            dados.get('data'), dados.get('hora'), dados.get('area'), dados.get('sistema'),
            dados.get('descricao'), dados.get('impacto'), dados.get('descumprimento'),
            dados.get('desc_detalhe'), dados.get('plano_acao'), dados.get('reincidencia'),
            rein_data, dados.get('risco'), dados.get('risco_desc'), dados.get('risco_valor'),
            dados.get('impacto_cliente'), dados.get('imp_cliente_desc'), dados.get('resp_plano'),
            prazo
        )

        self.cursor.execute(query, valores)
        
        # Recupera o ID gerado pelo SQL Server
        self.cursor.execute("SELECT @@IDENTITY AS id")
        novo_id = int(self.cursor.fetchone()[0])

        # Insere na tabela de histórico
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO Historico_Ocorrencias (ocorrencia_id, data_hora, status_novo, comentario) VALUES (?, ?, 'Aberto', 'Ocorrência registrada via Formulário Web.')",
            (novo_id, agora)
        )
        self.conn.commit()
        return novo_id

    def atualizar_status(self, id_ocorrencia, novo_status):
        if not self.conn: return
        
        self.cursor.execute("UPDATE Ocorrencias SET status = ? WHERE id = ?", (novo_status, id_ocorrencia))
        
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO Historico_Ocorrencias (ocorrencia_id, data_hora, status_novo, comentario) VALUES (?, ?, ?, 'Status modificado pelo sistema.')",
            (id_ocorrencia, agora, novo_status)
        )
        self.conn.commit()

# Instância única exportada para o app.py
db = DatabaseManager()





# -- Tabela principal de registros operacionais
# CREATE TABLE Ocorrencias (
#     id INT IDENTITY(1,1) PRIMARY KEY,
#     data DATE NOT NULL,
#     hora TIME NOT NULL,
#     area VARCHAR(100) NOT NULL,
#     sistema VARCHAR(100) NOT NULL,
#     descricao TEXT NOT NULL,
#     impacto TEXT NOT NULL,
#     status VARCHAR(50) DEFAULT 'Aberto',
#     descumprimento VARCHAR(3),
#     desc_detalhe TEXT,
#     plano_acao VARCHAR(3),
#     reincidencia VARCHAR(3),
#     rein_data DATE NULL,
#     risco VARCHAR(3),
#     risco_desc TEXT,
#     risco_valor VARCHAR(50),
#     impacto_cliente VARCHAR(3),
#     imp_cliente_desc TEXT,
#     resp_plano VARCHAR(100),
#     prazo DATE NULL
# );

# -- Tabela para guardar o rastro das alterações de status
# CREATE TABLE Historico_Ocorrencias (
#     id INT IDENTITY(1,1) PRIMARY KEY,
#     ocorrencia_id INT NOT NULL,
#     data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
#     status_novo VARCHAR(50) NOT NULL,
#     comentario TEXT,
#     CONSTRAINT FK_Ocorrencia_Historico FOREIGN KEY (ocorrencia_id) REFERENCES Ocorrencias(id)
# );