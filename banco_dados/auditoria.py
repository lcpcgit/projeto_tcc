import pandas as pd
from sqlalchemy import create_engine
import urllib.parse

# Configurações de exibição do Pandas
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 50)

# Credenciais
endpoint_aws = "hardwares-tcc.cveowcsuansb.sa-east-1.rds.amazonaws.com"
senha_aws = urllib.parse.quote_plus("milanhaverso2")
usuario_aws = "lcpctcc"
banco = "tcc_hardware"

url_conexao = f"mssql+pyodbc://{usuario_aws}:{senha_aws}@{endpoint_aws}/{banco}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(url_conexao)

print("🔍 Buscando os dados MAIS RECENTES da AWS...\n")

try:
    # 🚀 A MÁGICA ESTÁ AQUI: ORDER BY ... DESC
    query = """
    SELECT TOP 100 DataCaptura, Loja, Marca, Produto, Preco 
    FROM HistoricoPrecos 
    ORDER BY DataCaptura DESC
    """
    
    df_recentes = pd.read_sql(query, engine)
    
    print("🔥 AS 100 ÚLTIMAS LINHAS INJETADAS:")
    print(df_recentes)
    
except Exception as e:
    print(f"❌ Erro ao ler a AWS: {e}")