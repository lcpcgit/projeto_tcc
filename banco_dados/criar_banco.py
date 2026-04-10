import pyodbc

# Credenciais confirmadas!
endpoint_aws = "hardwares-tcc.cveowcsuansb.sa-east-1.rds.amazonaws.com"
senha_aws = "milanhaverso2" 
usuario_aws = "lcpctcc"

try:
    print("⏳ Conectando à AWS para criar o banco de dados do TCC...")
    # O autocommit=True é obrigatório no Python para comandos CREATE DATABASE
    conexao = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={endpoint_aws};"
        f"DATABASE=master;"
        f"UID={usuario_aws};"
        f"PWD={senha_aws}",
        autocommit=True 
    )
    cursor = conexao.cursor()
    
    # Cria o nosso próprio banco de dados!
    cursor.execute("CREATE DATABASE tcc_hardware")
    print("✅ SUCESSO! O banco 'tcc_hardware' foi criado na AWS!")
    
except Exception as e:
    print(f"❌ Erro: {e}")