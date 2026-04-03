import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
from bot_scraping import escanear_mercado_completo

# 1. Fazemos a busca de um produto de teste com a chave de salvar LIGADA
print("Iniciando o teste de injeção na nuvem...")
resultados = escanear_mercado_completo("rtx 5060", salvar_no_banco=True)

# 2. Vamos ler o banco de dados diretamente da AWS para provar que os dados chegaram lá!
print("\n🔍 Lendo os dados diretamente do SQL Server na AWS para confirmação...")

# DADOS REAIS DA SUA AWS:
endpoint_aws = "hardwares-tcc.cveowcsuansb.sa-east-1.rds.amazonaws.com"
senha_aws = "milanhaverso2" 
usuario_aws = "lcpctcc"

try:
    # Formato moderno e seguro de conexão
    senha_codificada = urllib.parse.quote_plus(senha_aws)
    url_conexao = f"mssql+pyodbc://{usuario_aws}:{senha_codificada}@{endpoint_aws}/tcc_hardware?driver=ODBC+Driver+17+for+SQL+Server"
    engine = create_engine(url_conexao)
    
    # Executa um SELECT diretamente na nuvem
    df_nuvem = pd.read_sql("SELECT TOP 5 * FROM HistoricoPrecos", con=engine)
    
    print("\n🎉 SUCESSO ABSOLUTO! Olha os 5 primeiros produtos que já estão na sua AWS:")
    print(df_nuvem[['Loja', 'Produto', 'Preco']])

except Exception as e:
    print(f"❌ Ocorreu um erro ao ler o banco: {e}")