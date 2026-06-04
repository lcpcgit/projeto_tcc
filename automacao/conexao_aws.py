from pathlib import Path
import os
import socket
import tomllib
import urllib.parse

from sqlalchemy import create_engine, event


CHAVES_OBRIGATORIAS = ("DB_HOST", "DB_USER", "DB_PASSWORD")


def _montar_segredos(origem):
    return {chave: origem[chave] for chave in CHAVES_OBRIGATORIAS}


def carregar_segredos_aws():
    segredos_ambiente = {
        chave: os.getenv(chave)
        for chave in CHAVES_OBRIGATORIAS
        if os.getenv(chave)
    }
    if len(segredos_ambiente) == len(CHAVES_OBRIGATORIAS):
        return _montar_segredos(segredos_ambiente)

    caminhos = [
        Path.cwd() / ".streamlit" / "secrets.toml",
        Path(__file__).resolve().parents[1] / ".streamlit" / "secrets.toml",
        Path(__file__).resolve().parents[2] / ".streamlit" / "secrets.toml",
    ]

    for caminho in caminhos:
        if caminho.exists():
            with caminho.open("rb") as arquivo:
                segredos = tomllib.load(arquivo)
            return _montar_segredos(segredos)

    raise FileNotFoundError("Arquivo .streamlit/secrets.toml nao encontrado.")


def _extrair_host_porta(db_host):
    host = str(db_host).strip()
    porta = 1433

    if host.lower().startswith("tcp:"):
        host = host[4:]

    if "\\" in host:
        host = host.split("\\", 1)[0]

    if "," in host:
        host, porta_texto = host.rsplit(",", 1)
        porta = int(porta_texto.strip())
    elif ":" in host and host.count(":") == 1:
        possivel_host, possivel_porta = host.rsplit(":", 1)
        if possivel_porta.isdigit():
            host = possivel_host
            porta = int(possivel_porta)

    return host.strip(" []"), porta


def verificar_alcance_sql_server(db_host, timeout=5):
    host, porta = _extrair_host_porta(db_host)
    timeout_tcp = max(1, min(float(timeout), 5))

    try:
        with socket.create_connection((host, porta), timeout=timeout_tcp):
            return
    except OSError as erro:
        raise TimeoutError(
            f"Nao foi possivel conectar em {host}:{porta} em {timeout_tcp:.0f}s. "
            "Verifique se o endpoint DB_HOST esta correto e se a porta 1433 esta "
            "liberada no firewall/Security Group da AWS para o seu IP atual."
        ) from erro


def criar_engine_aws(timeout=20):
    segredos = carregar_segredos_aws()
    verificar_alcance_sql_server(segredos["DB_HOST"], timeout=timeout)

    string_odbc = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={segredos['DB_HOST']};"
        "DATABASE=tcc_hardware;"
        f"UID={segredos['DB_USER']};"
        f"PWD={segredos['DB_PASSWORD']};"
        f"Login Timeout={timeout};"
        f"Connection Timeout={timeout};"
        "TrustServerCertificate=yes;"
    )
    url_conexao = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(string_odbc)}"
    engine = create_engine(
        url_conexao,
        pool_pre_ping=True,
        pool_recycle=1800,
        supports_comments=False,
        connect_args={"timeout": timeout},
    )

    @event.listens_for(engine, "connect", insert=True)
    def aplicar_timeout_conexao(dbapi_connection, connection_record):
        try:
            dbapi_connection.timeout = timeout
        except Exception:
            pass

    @event.listens_for(engine, "before_cursor_execute")
    def aplicar_timeout_cursor(conn, cursor, statement, parameters, context, executemany):
        try:
            cursor.timeout = timeout
        except Exception:
            pass

    return engine
