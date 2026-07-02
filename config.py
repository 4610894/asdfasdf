import pandas as pd
from datetime import date, timedelta
import holidays
import locale

# Caminhos e Constantes (Adaptadas para o backend web)
CAMINHO_ESC = None
CAMINHO_BTC = None
CAMINHO_RV = None
CAMINHO_BMF = None

# Configuração de feriados
feriados_br = holidays.Brazil(years=[2026, 2027, 2028, 2029, 2030], state='SP')
feriados = [pd.Timestamp(d) for d in feriados_br.keys()]
custom_bday = pd.offsets.CustomBusinessDay(holidays=feriados)

HOJE = date.today()
DATA = HOJE + custom_bday
DIA = DATA.day
MES = DATA.month
ANO = DATA.year

# Lidando com o locale de forma segura
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    MES_NOME = DATA.strftime('%B').upper()
    MES_ANT = (DATA.replace(day=1) - timedelta(days=1))
    MES_ANT_NOME = MES_ANT.strftime('%B').upper()
except:
    # Fallback caso o locale pt_BR não exista no servidor Windows do banco
    meses_pt = ["", "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", 
                "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
    MES_NOME = meses_pt[DATA.month]
    MES_ANT = (DATA.replace(day=1) - timedelta(days=1))
    MES_ANT_NOME = meses_pt[MES_ANT.month]

SERVER = None
DATABASE = None
USERNAME = None
PASSWORD = None

CONTAS_IMPESSOAIS = None
NOME_JANELA = 'Liquidação Inteligente'

# Cores originais mantidas para uso futuro ou logs
AZUL = '#312783'
AZUL_HOVER = '#0B215C'
