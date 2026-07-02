import os
import shutil
import subprocess
import tkinter as tk
import threading

# ================= CONFIGURAÇÕES =================
REDE_DIR = r"\\caminho\da\sua\pasta\de\rede\LiquidacaoApp"
LOCAL_DIR = os.path.join(os.environ['LOCALAPPDATA'], "LiquidacaoInteligente")
ARQUIVO_VERSAO = "versao.txt"
ARQUIVO_EXE = "Liquidacao_Main.exe"

def obter_versao(caminho_pasta):
    caminho_arquivo = os.path.join(caminho_pasta, ARQUIVO_VERSAO)
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, 'r') as f:
            return f.read().strip()
    return "0.0.0"

def exibir_tela_atualizacao(caminho_exe_rede, caminho_exe_local):
    """Exibe uma janela de carregamento enquanto copia os arquivos em segundo plano."""
    janela = tk.Tk()
    janela.title("Atualizador")
    
    # Remove as bordas da janela do Windows
    janela.overrideredirect(True)
    
    # Configura o tamanho e centraliza na tela
    largura, altura = 350, 100
    tela_largura = janela.winfo_screenwidth()
    tela_altura = janela.winfo_screenheight()
    x = (tela_largura // 2) - (largura // 2)
    y = (tela_altura // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")
    
    # Estilo da janela
    janela.configure(bg="#312783") # Azul Itaú
    
    lbl_titulo = tk.Label(janela, text="Liquidação Inteligente", font=("Arial", 12, "bold"), bg="#312783", fg="white")
    lbl_titulo.pack(pady=(15, 5))
    
    lbl_status = tk.Label(janela, text="Baixando nova atualização. Por favor, aguarde...", font=("Arial", 9), bg="#312783", fg="white")
    lbl_status.pack()

    # Função que fará a cópia em uma Thread separada para não travar a janela
    def tarefa_copia():
        try:
            shutil.copy2(caminho_exe_rede, caminho_exe_local)
            shutil.copy2(os.path.join(REDE_DIR, ARQUIVO_VERSAO), os.path.join(LOCAL_DIR, ARQUIVO_VERSAO))
        except Exception as e:
            pass # Se falhar, ignora e segue a vida
        finally:
            # Fecha a janela quando terminar a cópia
            janela.destroy()

    # Inicia a cópia em paralelo e mantém a interface rodando
    threading.Thread(target=tarefa_copia, daemon=True).start()
    janela.mainloop()

def atualizar_e_rodar():
    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)

    versao_local = obter_versao(LOCAL_DIR)
    
    try:
        versao_rede = obter_versao(REDE_DIR)
        
        # Se a versão da rede for diferente, chama a interface de atualização
        if versao_rede != versao_local and versao_rede != "0.0.0":
            caminho_exe_rede = os.path.join(REDE_DIR, ARQUIVO_EXE)
            caminho_exe_local = os.path.join(LOCAL_DIR, ARQUIVO_EXE)
            
            exibir_tela_atualizacao(caminho_exe_rede, caminho_exe_local)
            
    except Exception as e:
        pass # Erro de rede, continua silenciosamente

    # Executa o aplicativo principal
    exe_local = os.path.join(LOCAL_DIR, ARQUIVO_EXE)
    if os.path.exists(exe_local):
        subprocess.Popen([exe_local])
    else:
        # Se não tem o app local e não conseguiu baixar, avisa o usuário
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, "Aplicativo não encontrado. Verifique sua conexão com a rede corporativa.", "Erro de Inicialização", 0)

if __name__ == "__main__":
    atualizar_e_rodar()


# pyinstaller --noconfirm --onefile --windowed launcher.py




# import os
# import shutil
# import subprocess

# # ================= CONFIGURAÇÕES =================
# # Caminho na rede onde ficam as atualizações
# REDE_DIR = r"\\caminho\da\sua\pasta\de\rede\LiquidacaoApp"

# # Caminho local onde o app vai rodar (AppData do usuário)
# LOCAL_DIR = os.path.join(os.environ['LOCALAPPDATA'], "LiquidacaoInteligente")

# ARQUIVO_VERSAO = "versao.txt"
# ARQUIVO_EXE = "Liquidacao_Main.exe"

# def obter_versao(caminho_pasta):
#     caminho_arquivo = os.path.join(caminho_pasta, ARQUIVO_VERSAO)
#     if os.path.exists(caminho_arquivo):
#         with open(caminho_arquivo, 'r') as f:
#             return f.read().strip()
#     return "0.0.0"

# def atualizar_e_rodar():
#     if not os.path.exists(LOCAL_DIR):
#         os.makedirs(LOCAL_DIR)

#     versao_local = obter_versao(LOCAL_DIR)
    
#     try:
#         versao_rede = obter_versao(REDE_DIR)
        
#         # Se a versão da rede for diferente (ou maior), faz o download
#         if versao_rede != versao_local and versao_rede != "0.0.0":
#             caminho_exe_rede = os.path.join(REDE_DIR, ARQUIVO_EXE)
#             caminho_exe_local = os.path.join(LOCAL_DIR, ARQUIVO_EXE)
            
#             # Copia o executável e o txt de versão
#             shutil.copy2(caminho_exe_rede, caminho_exe_local)
#             shutil.copy2(os.path.join(REDE_DIR, ARQUIVO_VERSAO), os.path.join(LOCAL_DIR, ARQUIVO_VERSAO))
            
#     except Exception as e:
#         # Se der erro de rede (VPN caída, etc), ignora e tenta rodar o que já tem localmente
#         pass

#     # Executa o aplicativo principal localmente
#     exe_local = os.path.join(LOCAL_DIR, ARQUIVO_EXE)
#     if os.path.exists(exe_local):
#         subprocess.Popen([exe_local])
#     else:
#         # Aqui você pode usar uma biblioteca como tkinter ou ctypes para exibir um erro na tela
#         print("Erro: Aplicativo não encontrado e sem conexão com a rede.")

# if __name__ == "__main__":
#     atualizar_e_rodar()