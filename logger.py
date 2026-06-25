import datetime

class WebLogger:
    """
    Versão adaptada do Logger para o ambiente Web/Eel.
    Em vez de usar filas do Tkinter, ele guarda os logs e os envia via Eel
    ou deixa disponíveis para a interface HTML buscar.
    """
    def __init__(self):
        self.historico = []

    def log(self, message: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.historico.append(log_entry)
        print(log_entry) # Imprime no console do servidor
        
        # Opcional: Se quiser que o log vá para a tela HTML em tempo real, 
        # poderia chamar uma função JS aqui usando eel.atualizar_log(log_entry)
        
    def obter_logs_recentes(self, quantidade=50):
        return self.historico[-quantidade:]
        
    def limpar_logs(self):
        self.historico = []

# Instância global do logger
sistema_logger = WebLogger()
