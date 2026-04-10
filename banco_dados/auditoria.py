import pandas as pd
from sqlalchemy import create_engine
import urllib.parse

# Suas credenciais da AWS
endpoint_aws = "hardwares-tcc.cveowcsuansb.sa-east-1.rds.amazonaws.com"
senha_aws = urllib.parse.quote_plus("milanhaverso2")
usuario_aws = "lcpctcc"
banco = "tcc_hardware"

# Cria o motor de conexão
url_conexao = f"mssql+pyodbc://{usuario_aws}:{senha_aws}@{endpoint_aws}/{banco}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(url_conexao)

print("🔍 Conectando à AWS para auditar o banco de dados...")

try:
    # Lê a tabela inteira da nuvem para um DataFrame
    df = pd.read_sql("SELECT * FROM HistoricoPrecos", engine)
    
    print("\n✅ SUCESSO! Leitura da nuvem confirmada.")
    print(f"📊 TOTAL DE REGISTROS NA AWS: {len(df)} linhas de histórico.")
    
    print("\n🔥 OS 5 ÚLTIMOS PRODUTOS QUE O ROBÔ INJETOU:")
    # Pega as últimas 5 linhas e mostra só as colunas mais importantes
    print(df.tail(5)[['DataCaptura', 'Loja', 'Produto', 'Preco']])
    
except Exception as e:
    print(f"❌ Erro ao ler a AWS: {e}")