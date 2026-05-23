import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import urllib.parse
import unicodedata
import re
import numpy as np
import time

st.set_page_config(page_title="Hardware Preditivo", layout="wide")

# ================= CONFIGURAÇÃO VISUAL DE DESIGN =================
st.markdown("""
<style>
    :root {
        --bg: #121212;
        --panel: #0D2137;
        --panel-soft: #111A25;
        --surface: #1A1A1A;
        --surface-2: #242424;
        --blue: #0D4E86;
        --blue-line: #0066CC;
        --red: #9D1F1F;
        --red-line: #FF4B4B;
        --text: #FFFFFF;
        --muted: #AAB4C0;
    }

    .stApp {
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }

    header[data-testid="stHeader"] {
        background-color: var(--bg) !important;
    }

    section[data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 1480px;
        padding-top: 1.6rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    hr {
        border-color: rgba(255, 255, 255, 0.12) !important;
    }

    div[data-testid="stButton"] > button {
        background-color: var(--surface-2) !important;
        color: var(--text) !important;
        border: 1px solid #303030 !important;
        border-radius: 6px !important;
        min-height: 42px;
        transition: all 0.2s ease !important;
        white-space: nowrap;
    }

    div[data-testid="stButton"] > button:hover {
        border-color: var(--red-line) !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 0 1px rgba(255, 75, 75, 0.25) !important;
    }

    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: var(--red) !important;
        border-color: var(--red-line) !important;
    }

    .st-key-nav_pesquisa button,
    .st-key-nav_predicao button,
    .st-key-nav_dados button {
        min-width: 158px;
        font-weight: 600 !important;
    }

    .st-key-nav_pesquisa button[kind="primary"],
    .st-key-nav_predicao button[kind="primary"],
    .st-key-nav_dados button[kind="primary"] {
        background-color: var(--blue) !important;
        border-color: var(--blue) !important;
    }

    .top-nav-line {
        border-bottom: 1px solid rgba(0, 102, 204, 0.35);
        margin: 0.5rem 0 1.4rem 0;
    }

    div[data-testid="column"]:has(.filter-panel-marker) {
        background-color: var(--panel);
        border-left: 1px solid var(--blue-line);
        padding: 1rem 1.1rem 1.5rem 1.1rem;
        min-height: calc(100vh - 112px);
        margin-top: -0.35rem;
    }

    .filter-panel-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }

    .filter-separator {
        height: 1px;
        background: rgba(255, 255, 255, 0.10);
        margin: 0.75rem 0 1rem 0;
    }

    .helper-copy {
        color: var(--muted);
        font-size: 0.92rem;
        line-height: 1.35;
        margin-bottom: 1rem;
    }

    .section-eyebrow {
        color: #D7E7FF;
        font-size: 0.92rem;
        font-weight: 700;
        margin: 1rem 0 0.65rem 0;
    }

    .chart-placeholder {
        min-height: 360px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        background: rgba(51, 0, 0, 0.22);
        border: 1px solid rgba(255, 75, 75, 0.16);
        border-radius: 6px;
        color: #FF5D5D;
        padding: 2rem;
        margin-top: 1rem;
    }

    .data-panel {
        background: rgba(13, 33, 55, 0.65);
        border-left: 5px solid var(--blue-line);
        border-radius: 8px;
        color: #94B3FD;
        padding: 1rem;
        margin: 1rem 0;
    }

    .danger-panel {
        background: #330000;
        border-left: 5px solid #FF0000;
        border-radius: 8px;
        color: #FFFFFF;
        padding: 1rem;
        margin: 1rem 0;
    }

    .success-panel {
        background-color: #1A1A1A;
        border-left: 5px solid var(--red-line);
        border-radius: 8px;
        color: #FFFFFF;
        padding: 1rem;
        margin: 1rem 0;
    }

    .stAlert {
        background-color: var(--panel) !important;
        color: #94B3FD !important;
        border-left: 5px solid var(--blue-line) !important;
        border-radius: 8px !important;
    }

    button[data-baseweb="tab"] {
        color: #CCCCCC !important;
    }

    button[aria-selected="true"] {
        color: var(--red-line) !important;
        border-bottom-color: var(--red-line) !important;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] > input,
    input,
    textarea {
        background-color: var(--surface) !important;
        color: var(--text) !important;
    }

    @media (max-width: 900px) {
        [data-testid="stAppViewContainer"] .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        div[data-testid="column"]:has(.filter-panel-marker) {
            min-height: auto;
            border-left: none;
            border-top: 1px solid var(--blue-line);
            margin-top: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ================= VARIÁVEIS GLOBAIS (Dicionários e Categorias) =================
categorias_base = [
    "Placa de Vídeo", "Processador", "Placa Mãe", "Memória RAM", "SSD", "HD", 
    "Monitor", "Fonte", "Gabinete", "Water Cooler", "Air Cooler", "Fan",
    "Mouse Gamer", "Mouse", "Teclado Mecânico", "Teclado Magnético", "Headset Gamer",
    "Mousepad Gamer", "Webcam", "Soundbar", "Microfone"
]

mapa_subcategorias = {
    "Placa de Vídeo": [
        "GT 610", "GT 730", "GT 740", "GTX 750 Ti", "GTX 960", "GTX 1050 Ti", 
        "GTX 1650", "GTX 1650 Ti", "GTX 1660", "GTX 1660 Ti", "GTX 1660 Super", 
        "RTX 2060", "RTX 2080", "RTX 2080 Super", "RTX 3050", "RTX 3060", 
        "RTX 4060", "RTX 4060 Ti", "RTX 5050", "RTX 5060", "RTX 5060 Ti", 
        "RTX 5070", "RTX 5070 Ti", "RTX 5080", "RTX 5090", 
        "RX 550", "RX 560", "RX 570", "RX 580", "RX 590", "RX 6400", "RX 6500 XT", 
        "RX 6600", "RX 6750 XT", "RX 7600", "RX 7600 XT", "RX 7700 XT", 
        "RX 9060", "RX 9060 XT", "RX 9070", "RX 9070 GRE", "RX 9070 XT",
        "Arc A380", "Arc A580", "Arc A750", "Arc A770", "Arc B570", "Arc B580"
    ],
    "Processador": [
        "Ryzen 3 4100", "Ryzen 5 4500", "Ryzen 5 5600", "Ryzen 5 5600X", 
        "Ryzen 5 5600G", "Ryzen 5 5600GT", "Ryzen 7 5700", "Ryzen 7 5700X", 
        "Ryzen 7 5700G", "Ryzen 7 5800", "Ryzen 7 5800X", "Ryzen 9 5900X", 
        "Ryzen 5 7600", "Ryzen 5 7600X", "Ryzen 7 7700X", "Ryzen 7 7800X3D", 
        "Ryzen 9 7900", "Ryzen 9 7900X", "Ryzen 9 7950X", "Ryzen 5 8500G", 
        "Ryzen 5 8600G", "Ryzen 7 8700G", "Ryzen 5 9600X", "Ryzen 7 9700X", 
        "Ryzen 9 9900X", "Ryzen 9 9950X", "Ryzen 9 9900X3D", "Ryzen 9 9950X3D",
        "Core i3 12100F", "Core i5 12400F", "Core i5 12600K", "Core i7 12700K", "Core i9 12900K",
        "Core i3 13100F", "Core i5 13400F", "Core i5 13600K", "Core i7 13700K",
        "Core i3 14100F", "Core i5 14400F", "Core i5 14600K", "Core i5 14600KF", 
        "Core i7 14700K", "Core i7 14700KF", "Core i9 14900K",
        "Core Ultra 5 245K", "Core Ultra 5 245KF", "Core Ultra 7 265K", 
        "Core Ultra 7 265KF", "Core Ultra 9 285K"
    ],
    "Placa Mãe": [
        "A320M", "A520M", "B450M", "B450", "B550M", "B550", "A620M", 
        "B650M", "B650", "B650E", "X670", "X870", "X870E", 
        "H610M", "B660M", "B760M", "B760", "Z690", "Z790", "Z890", "Z890M"
    ],
    "Memória RAM": [
        "8GB DDR4", "8GB DDR5", 
        "16GB DDR4", "16GB DDR5", 
        "32GB DDR4", "32GB DDR5", 
        "64GB DDR4", "64GB DDR5"
    ],
    "SSD": ["480GB", "500GB", "1TB", "2TB", "4TB"],
    "HD": ["1TB", "2TB", "4TB"],
    "Monitor": ["75hz", "100hz", "144hz", "165hz", "240hz", "280hz", "360hz", "2K", "4K", "Ultrawide"],
    "Fonte": ["500w", "600w", "650w", "750w", "850w", "1000w", "1200w"],
    "Gabinete": ["Aquario", "Mid Tower", "Full Tower", "Mini ITX"],
    "Water Cooler": ["120mm", "240mm", "360mm"],
    "Fan": ["120mm", "140mm", "RGB"],
    "Mouse Gamer": [], "Mouse": [], "Teclado Mecânico": [], "Teclado Magnético": [], 
    "Headset Gamer": [], "Mousepad Gamer": [], "Webcam": [], "Soundbar": [], "Microfone": []
}

# ================= FUNÇÕES DE DADOS =================
@st.cache_data(ttl=600) 
def carregar_dados_aws():
    endpoint_aws = "hardwares-tcc.cveowcsuansb.sa-east-1.rds.amazonaws.com"
    senha_aws = urllib.parse.quote_plus("milanhaverso2")
    usuario_aws = "lcpctcc"
    url_conexao = f"mssql+pyodbc://{usuario_aws}:{senha_aws}@{endpoint_aws}/tcc_hardware?driver=ODBC+Driver+17+for+SQL+Server"
    
    try:
        engine = create_engine(url_conexao)
        
        df_precos = pd.read_sql("SELECT DataCaptura, Loja, Marca, Produto, Preco FROM HistoricoPrecos", engine) 
        df_dolar = pd.read_sql("SELECT DataCaptura, ValorDolar AS Dolar FROM HistoricoDolar", engine)
        
        if df_dolar['Dolar'].dtype == 'object':
            df_dolar['Dolar'] = df_dolar['Dolar'].str.replace(',', '.').astype(float)
        
        df_precos['DataCaptura'] = pd.to_datetime(df_precos['DataCaptura']).dt.normalize()
        df_dolar['DataCaptura'] = pd.to_datetime(df_dolar['DataCaptura']).dt.normalize()
        
        df = pd.merge(df_precos, df_dolar, on='DataCaptura', how='left')
        
        df = df.sort_values('DataCaptura')
        df['Dolar'] = df['Dolar'].ffill().bfill()
        
        palavras_proibidas = 'MÁQUINA|MAQUINA|MONTAGEM|COMPUTADOR|PC GAMER|COMPLETO|COMPLETA|CPU GAMER|DESKTOP'
        df = df[~df['Produto'].str.contains(palavras_proibidas, case=False, na=False)]
        
        import re
        df['Produto'] = df['Produto'].apply(lambda x: re.sub(r'^[\d\s-]+\s*', '', str(x)))
        
        return df
    except Exception as e:
        st.markdown(f"""
        <div style="background-color: #330000; padding: 15px; border-radius: 8px; border-left: 5px solid #FF0000; color: #FFF;">
            🚨 <b>Erro:</b> Erro ao conectar na AWS: {e}
        </div>
        """, unsafe_allow_html=True)
        return pd.DataFrame()

# ================= FUNÇÕES DE INTERFACE =================
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def iniciar_painel_filtros(titulo="Filtros"):
    st.markdown('<span class="filter-panel-marker"></span>', unsafe_allow_html=True)
    st.markdown(f'<div class="filter-panel-title">{titulo}</div>', unsafe_allow_html=True)
    st.markdown('<div class="filter-separator"></div>', unsafe_allow_html=True)


def texto_apoio(texto):
    st.markdown(f'<div class="helper-copy">{texto}</div>', unsafe_allow_html=True)


def titulo_secao_filtro(texto):
    st.markdown(f'<div class="section-eyebrow">{texto}</div>', unsafe_allow_html=True)


def painel_info(texto):
    st.markdown(f'<div class="data-panel">{texto}</div>', unsafe_allow_html=True)


def painel_erro(texto):
    st.markdown(f'<div class="danger-panel">{texto}</div>', unsafe_allow_html=True)


def painel_sucesso(texto):
    st.markdown(f'<div class="success-panel">{texto}</div>', unsafe_allow_html=True)


def placeholder_grafico(texto):
    st.markdown(f'<div class="chart-placeholder"><div>{texto}</div></div>', unsafe_allow_html=True)


def configurar_grafico_preco(fig, dados, coluna="Preco", altura=440):
    valores = pd.to_numeric(dados[coluna], errors="coerce").dropna()
    if not valores.empty:
        menor = valores.min()
        maior = valores.max()
        if menor == maior:
            folga = max(abs(menor) * 0.1, 1)
            fig.update_yaxes(range=[menor - folga, maior + folga])
        else:
            fig.update_yaxes(range=[menor * 0.9, maior * 1.1])

    fig.update_layout(
        height=altura,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF"),
        margin=dict(l=20, r=20, t=70, b=40),
        xaxis=dict(showgrid=True, gridcolor="#333333"),
        yaxis=dict(showgrid=True, gridcolor="#333333", title="Preço (R$)")
    )
    fig.update_xaxes(tickformat="%d/%m/%Y", showgrid=True, gridcolor="#333333")
    return fig


def renderizar_menu_superior(pagina_atual, paginas):
    col_nav_1, col_nav_2, col_nav_3, col_spacer = st.columns([1, 1, 1, 3.5], gap="small")
    itens = [
        (col_nav_1, paginas[0], "Pesquisa de Mercado", "nav_pesquisa"),
        (col_nav_2, paginas[1], "Sistema de predição", "nav_predicao"),
        (col_nav_3, paginas[2], "Gestão de Dados", "nav_dados"),
    ]

    for coluna, pagina, rotulo, chave in itens:
        with coluna:
            ativo = pagina_atual == pagina
            if st.button(
                rotulo,
                key=chave,
                type="primary" if ativo else "secondary",
                width="stretch",
            ) and not ativo:
                st.switch_page(pagina)

    with col_spacer:
        st.empty()

    st.markdown('<div class="top-nav-line"></div>', unsafe_allow_html=True)


def limpar_texto_busca(texto):
    if not isinstance(texto, str):
        return ""
    texto = "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
    texto = texto.lower().strip()
    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto


def aplicar_filtro_exclusivo(nome_do_produto, palavras_da_pesquisa):
    if "mouse" in palavras_da_pesquisa and "gamer" not in palavras_da_pesquisa:
        return "mouse" in nome_do_produto and "gamer" not in nome_do_produto
    return all(palavra in nome_do_produto for palavra in palavras_da_pesquisa)


def opcoes_modelo_por_categoria(cat_escolhida):
    todos_os_modelos = sorted(list(set(sum(mapa_subcategorias.values(), []))))
    if cat_escolhida:
        modelos_da_cat = mapa_subcategorias.get(cat_escolhida, [])
        if len(modelos_da_cat) > 0:
            return [""] + sorted(modelos_da_cat), False
        return ["N/A"], True
    return [""] + todos_os_modelos, False


def aplicar_filtro_categoria(df_drill, cat_escolhida):
    if not cat_escolhida:
        return df_drill

    termo_cat_limpo = "".join(
        c for c in unicodedata.normalize("NFD", cat_escolhida) if unicodedata.category(c) != "Mn"
    ).lower()
    produto_lower = df_drill["Produto"].str.lower()

    if termo_cat_limpo == "placa de video":
        df_drill = df_drill[produto_lower.str.contains("video|vídeo|vga|geforce|radeon|rtx|gtx|rx|arc|gpu", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("placa mae|placa-mae|cooler|water|espelho|suporte|cabo|fonte|mouse|teclado|monitor|headset|cadeira|mesa|ssd|hd ", na=False)]

    elif termo_cat_limpo == "processador":
        df_drill = df_drill[produto_lower.str.contains("processador|ryzen|core i|athlon|celeron|pentium", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("placa|cooler|water|fan|gabinete|memoria|notebook|pc|computador|desktop|mouse|teclado|monitor|headset|fonte|ssd|hd |gpu", na=False)]

    elif termo_cat_limpo == "placa mae":
        df_drill = df_drill[produto_lower.str.contains("placa|motherboard|mainboard", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("video|vídeo|cooler|mouse|teclado|monitor|headset|fonte|processador|gpu", na=False)]

    elif termo_cat_limpo == "memoria ram":
        df_drill = df_drill[produto_lower.str.contains("memoria|ram|ddr", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("placa|video|vídeo|cooler|mouse|teclado|monitor|headset|fonte|processador|gpu|gddr", na=False)]

    elif "fonte" in termo_cat_limpo:
        df_drill = df_drill[produto_lower.str.contains("fonte|atx|power", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("cabo|adaptador|placa|video|cooler|mouse|teclado|monitor|headset|processador|memoria", na=False)]

    elif termo_cat_limpo == "monitor":
        df_drill = df_drill[produto_lower.str.contains("monitor|tela|display", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("cabo|hdmi|adaptador|suporte|braco|braço|pistao|pistão|tv|televisao|televisão|placa", na=False)]

    elif termo_cat_limpo == "ssd":
        df_drill = df_drill[produto_lower.str.contains(r"ssd|nvme|m\.2|sata", na=False, regex=True)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains(r"cabo|adaptador|dissipador|heatsink|case|gaveta|placa|cooler|\bhd\b|disco rigido|hard drive", na=False, regex=True)]

    elif termo_cat_limpo == "hd":
        df_drill = df_drill[produto_lower.str.contains("hd |disco rigido|hard drive|hd externo", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("ssd|cabo|adaptador|gaveta|case|monitor|tv|placa", na=False)]

    elif termo_cat_limpo == "water cooler":
        df_drill = df_drill[produto_lower.str.contains("water cooler|watercooler|liquid cooler", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("gabinete|placa|processador|fan|ventoinha|ar", na=False)]

    elif termo_cat_limpo == "air cooler":
        df_drill = df_drill[produto_lower.str.contains("air cooler|aircooler|cooler para processador", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("water|liquido|gabinete|fan |ventoinha", na=False)]

    elif termo_cat_limpo == "fan":
        df_drill = df_drill[produto_lower.str.contains("fan|ventoinha|cooler para gabinete", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("water|air|processador|gabinete|placa", na=False)]

    elif termo_cat_limpo == "gabinete":
        df_drill = df_drill[produto_lower.str.contains("gabinete|case", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("cooler|fan|ventoinha|placa|fonte|memoria", na=False)]

    elif termo_cat_limpo == "headset gamer":
        df_drill = df_drill[produto_lower.str.contains("headset|fone", na=False) & produto_lower.str.contains("gamer", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("suporte|mouse|teclado|cadeira|mesa", na=False)]

    elif termo_cat_limpo == "mouse":
        df_drill = df_drill[produto_lower.str.contains("mouse", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("gamer|mousepad|pad|teclado|headset|monitor|placa|cooler|fonte|memoria|processador", na=False)]

    elif termo_cat_limpo == "mouse gamer":
        df_drill = df_drill[produto_lower.str.contains("mouse", na=False) & produto_lower.str.contains("gamer", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("mousepad|pad|teclado|headset|monitor|placa|cooler|fonte|memoria|processador", na=False)]

    elif termo_cat_limpo == "teclado mecanico":
        df_drill = df_drill[produto_lower.str.contains("teclado", na=False) & produto_lower.str.contains("mecanico|mecânico", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("mouse|kit|combo", na=False)]

    elif termo_cat_limpo == "teclado magnetico":
        df_drill = df_drill[produto_lower.str.contains("teclado", na=False) & produto_lower.str.contains("magnetico|magnético", na=False)]
        df_drill = df_drill[~df_drill["Produto"].str.lower().str.contains("mouse|kit|combo", na=False)]

    else:
        for palavra in termo_cat_limpo.split():
            df_drill = df_drill[df_drill["Produto"].str.lower().str.contains(palavra, na=False)]

    return df_drill


def aplicar_filtro_modelo(df_drill, cat_escolhida, subcat_escolhida):
    if not subcat_escolhida or subcat_escolhida == "N/A":
        return df_drill

    mask = pd.Series(True, index=df_drill.index)
    partes_busca = subcat_escolhida.lower().split()

    for parte in partes_busca:
        padrao_parte = r"\b" + re.escape(parte) + r"\b"
        if parte.isdigit():
            padrao_parte = re.escape(parte)
        elif parte.endswith("tb") or parte.endswith("gb"):
            padrao_parte = r"(?<![a-z0-9])" + re.escape(parte) + r"(?![a-z0-9])"
        mask = mask & df_drill["Produto"].str.lower().str.contains(padrao_parte, regex=True, na=False)

    modelos_derivados = []
    todos_os_modelos = sorted(list(set(sum(mapa_subcategorias.values(), []))))
    lista_para_verificar = mapa_subcategorias.get(cat_escolhida, todos_os_modelos) if cat_escolhida else todos_os_modelos

    for modelo in lista_para_verificar:
        if modelo != subcat_escolhida and subcat_escolhida.lower() in modelo.lower():
            modelos_derivados.append(modelo)

    for derivado in modelos_derivados:
        mask_derivado = pd.Series(True, index=df_drill.index)
        for parte in derivado.lower().split():
            padrao_parte_excl = r"\b" + re.escape(parte) + r"\b"
            if parte.isdigit():
                padrao_parte_excl = re.escape(parte)
            elif parte.endswith("tb") or parte.endswith("gb"):
                padrao_parte_excl = r"(?<![a-z0-9])" + re.escape(parte) + r"(?![a-z0-9])"
            mask_derivado = mask_derivado & df_drill["Produto"].str.lower().str.contains(padrao_parte_excl, regex=True, na=False)

        mask = mask & ~mask_derivado

    return df_drill[mask]


def aplicar_filtro_preco(df_drill, filtro_preco):
    if filtro_preco == "Abaixo de R$ 100":
        return df_drill[df_drill["Preco"] < 100]
    if filtro_preco == "R$ 100 a R$ 500":
        return df_drill[(df_drill["Preco"] >= 100) & (df_drill["Preco"] <= 500)]
    if filtro_preco == "R$ 500 a R$ 1.500":
        return df_drill[(df_drill["Preco"] > 500) & (df_drill["Preco"] <= 1500)]
    if filtro_preco == "R$ 1.500 a R$ 3.000":
        return df_drill[(df_drill["Preco"] > 1500) & (df_drill["Preco"] <= 3000)]
    if filtro_preco == "R$ 3.000 a R$ 5.000":
        return df_drill[(df_drill["Preco"] > 3000) & (df_drill["Preco"] <= 5000)]
    if filtro_preco == "R$ 5.000 a R$ 8.000":
        return df_drill[(df_drill["Preco"] > 5000) & (df_drill["Preco"] <= 8000)]
    if filtro_preco == "Acima de R$ 8.000":
        return df_drill[df_drill["Preco"] > 8000]
    return df_drill


# ================= PÁGINAS =================
def pagina_pesquisa_mercado():
    df_historico = carregar_dados_aws()
    conteudo_col, filtros_col = st.columns([4.4, 1.25], gap="large")

    with conteudo_col:
        st.title("Scanner")
        st.write("Acompanhe o histórico de preços praticados pelas maiores lojas de hardware do Brasil (Kabum e Terabyte).")

    if df_historico.empty:
        with filtros_col:
            iniciar_painel_filtros()
            texto_apoio("Não foi possível carregar os dados da AWS para alimentar os filtros.")
        with conteudo_col:
            painel_erro("<b>Atenção:</b> nenhum dado histórico foi encontrado para montar os gráficos.")
        return

    with filtros_col:
        iniciar_painel_filtros()
        st.write("Nível de análise para Tendência de Preços")
        modo_visao = st.radio(
            "Nível de análise para Tendência de Preços",
            ["Visão Geral", "Visão Específica"],
            horizontal=True,
            label_visibility="collapsed",
            key="mercado_modo_visao",
        )

        texto_apoio("Use os filtros para gerar os gráficos ao lado.")

        familia_input = ""
        produto_escolhido = ""
        esta_bloqueado = True

        if modo_visao == "Visão Geral":
            if "ultima_busca" not in st.session_state:
                st.session_state["ultima_busca"] = "rtx 5070"
            familia_input = st.text_input(
                "Família/marca do produto",
                value=st.session_state["ultima_busca"],
                key="mercado_familia_geral",
            )
            st.session_state["ultima_busca"] = familia_input
        else:
            pesquisa_produto = st.text_input(
                "Família/marca do produto",
                key="mercado_pesquisa_especifica",
                placeholder="Ex: RTX 4060 ASUS",
            )
            if pesquisa_produto:
                termos_busca = pesquisa_produto.lower().split()
                mask = pd.Series(True, index=df_historico.index)

                for termo in termos_busca:
                    mask = mask & df_historico["Produto"].str.lower().str.contains(termo, na=False, regex=False)

                if "ti" not in termos_busca:
                    mask = mask & ~df_historico["Produto"].str.lower().str.contains(r"(?<![a-z])ti(?![a-z])", regex=True, na=False)
                if "super" not in termos_busca:
                    mask = mask & ~df_historico["Produto"].str.lower().str.contains(r"(?<![a-z])super(?![a-z])", regex=True, na=False)
                if "xt" not in termos_busca:
                    mask = mask & ~df_historico["Produto"].str.lower().str.contains(r"(?<![a-z])xt(?![a-z])", regex=True, na=False)

                lista_filtrada = df_historico[mask]["Produto"].astype(str).str.strip().dropna().unique()
                lista_filtrada = sorted(lista_filtrada)
                if len(lista_filtrada) == 0:
                    lista_filtrada = ["Nenhum produto encontrado com esses termos."]
            else:
                lista_filtrada = ["Digite algo na pesquisa acima para encontrar o produto"]

            esta_bloqueado = len(lista_filtrada) == 1 and (
                lista_filtrada[0].startswith("Digite algo") or lista_filtrada[0].startswith("Nenhum produto")
            )
            produto_escolhido = st.selectbox(
                "Hardware específico",
                lista_filtrada,
                disabled=esta_bloqueado,
                key="mercado_produto_especifico",
            )

        st.markdown('<div class="filter-separator"></div>', unsafe_allow_html=True)
        titulo_secao_filtro("Filtros avançados")
        texto_apoio("Preencha pelo menos duas opções para visualizar o histórico de preços.")

        cat_escolhida = st.selectbox(
            "Categoria",
            [""] + sorted(categorias_base),
            key="mercado_categoria",
        )
        opcoes_modelo, disabled_mod = opcoes_modelo_por_categoria(cat_escolhida)
        subcat_escolhida = st.selectbox(
            "Modelo",
            opcoes_modelo,
            disabled=disabled_mod,
            key="mercado_modelo",
        )

        df_base_marcas = aplicar_filtro_categoria(df_historico.copy(), cat_escolhida)
        df_base_marcas = aplicar_filtro_modelo(df_base_marcas, cat_escolhida, subcat_escolhida)
        marcas_validas = sorted([m for m in df_base_marcas["Marca"].dropna().unique()])

        marcas_escolhidas = st.multiselect(
            "Marcas",
            marcas_validas,
            key="mercado_marcas",
        )
        especificacao_extra = st.text_input(
            "Especificação",
            key="mercado_especificacao",
            placeholder="Ex: Branco, OC",
        )
        filtro_preco = st.selectbox(
            "Faixa de Preço",
            [
                "Todos os Preços",
                "Abaixo de R$ 100",
                "R$ 100 a R$ 500",
                "R$ 500 a R$ 1.500",
                "R$ 1.500 a R$ 3.000",
                "R$ 3.000 a R$ 5.000",
                "R$ 5.000 a R$ 8.000",
                "Acima de R$ 8.000",
            ],
            key="mercado_faixa_preco",
        )

    df_drill = df_base_marcas.copy()
    if len(marcas_escolhidas) > 0:
        df_drill = df_drill[df_drill["Marca"].isin(marcas_escolhidas)]

    if especificacao_extra:
        espec_limpa = "".join(
            c for c in unicodedata.normalize("NFD", especificacao_extra) if unicodedata.category(c) != "Mn"
        ).lower()
        df_drill = df_drill[df_drill["Produto"].str.lower().str.contains(espec_limpa, na=False)]

    df_drill = aplicar_filtro_preco(df_drill, filtro_preco)

    filtros_ativos = 0
    if cat_escolhida:
        filtros_ativos += 1
    if subcat_escolhida and subcat_escolhida != "N/A":
        filtros_ativos += 1
    if len(marcas_escolhidas) > 0:
        filtros_ativos += 1
    if especificacao_extra:
        filtros_ativos += 1

    with conteudo_col:
        st.markdown("### Tendência de Preços")

        if modo_visao == "Visão Geral":
            if familia_input.strip():
                busca_limpa = limpar_texto_busca(familia_input)
                palavras_busca = busca_limpa.split()
                df_busca = df_historico.copy()
                df_busca["ProdutoLimpo"] = df_busca["Produto"].apply(limpar_texto_busca)
                mascara_filtro = df_busca["ProdutoLimpo"].apply(
                    lambda nome: aplicar_filtro_exclusivo(nome, palavras_busca)
                )
                df_filtrado = df_busca[mascara_filtro].copy()

                if not df_filtrado.empty:
                    df_agrupado = df_filtrado.groupby(["DataCaptura", "Loja"])["Preco"].mean().reset_index()
                    df_agrupado["Preco_Label"] = df_agrupado["Preco"].apply(formatar_moeda)

                    fig = px.line(
                        df_agrupado,
                        x="DataCaptura",
                        y="Preco",
                        color="Loja",
                        markers=True,
                        text="Preco_Label",
                        title=f"Média de Mercado da Família: {familia_input.upper()}",
                        labels={"DataCaptura": "Data", "Preco": "Preço (R$)", "Loja": "Loja"},
                    )
                    fig.update_traces(
                        textposition="top center",
                        hovertemplate="<b>Loja:</b> %{data.name}<br><b>Data da Extração:</b> %{x|%d/%m/%Y}<br><b>Média:</b> R$ %{y:,.2f}<extra></extra>",
                    )
                    st.plotly_chart(configurar_grafico_preco(fig, df_agrupado), use_container_width=True)
                else:
                    placeholder_grafico(f"Sem dados históricos para a família '{familia_input}'.")
            else:
                placeholder_grafico("Digite uma família/marca no painel de filtros para visualizar este gráfico.")

        else:
            if produto_escolhido and not esta_bloqueado:
                df_filtrado = df_historico[
                    df_historico["Produto"].astype(str).str.strip() == produto_escolhido
                ].copy()

                if not df_filtrado.empty:
                    df_filtrado["Preco_Label"] = df_filtrado["Preco"].apply(formatar_moeda)
                    fig = px.line(
                        df_filtrado,
                        x="DataCaptura",
                        y="Preco",
                        color="Loja",
                        markers=True,
                        text="Preco_Label",
                        title=f"Histórico Específico: {produto_escolhido}",
                        labels={"DataCaptura": "Data da Extração", "Preco": "Preço à Vista (R$)", "Loja": "Loja Monitorada"},
                    )
                    fig.update_traces(
                        textposition="top center",
                        hovertemplate="<b>Loja:</b> %{data.name}<br><b>Data da Extração:</b> %{x|%d/%m/%Y}<br><b>Preço:</b> R$ %{y:,.2f}<extra></extra>",
                    )
                    st.plotly_chart(configurar_grafico_preco(fig, df_filtrado), use_container_width=True)
                else:
                    placeholder_grafico("Sem dados suficientes para gerar o gráfico deste produto específico.")
            else:
                placeholder_grafico("Selecione a Família/Marca e Hardware específico para visualizar este gráfico.")

        st.markdown("---")
        st.markdown("### Análise de Filtros Avançados")
        st.write("Filtre o mercado através de categorias, modelos, marcas e especificações.")

        if filtros_ativos < 2:
            placeholder_grafico("Preencha pelo menos duas opções no painel de filtros para visualizar o histórico de preços.")
        elif df_drill.empty:
            placeholder_grafico("Nenhum hardware foi encontrado com essa combinação exata de filtros.")
        else:
            if subcat_escolhida != "" and subcat_escolhida != "N/A":
                df_agrupado_drill = df_drill.groupby(["DataCaptura", "Loja", "Marca"])["Preco"].mean().reset_index()
                df_agrupado_drill["Legenda"] = df_agrupado_drill["Marca"]
            else:
                df_agrupado_drill = df_drill.groupby(["DataCaptura", "Loja", "Produto"])["Preco"].mean().reset_index()
                df_agrupado_drill["Produto_Curto"] = df_agrupado_drill["Produto"].apply(
                    lambda x: x[:40] + "..." if len(x) > 40 else x
                )
                df_agrupado_drill["Legenda"] = df_agrupado_drill["Produto_Curto"]

            df_agrupado_drill["Preco_Label"] = df_agrupado_drill["Preco"].apply(formatar_moeda)

            partes_titulo = []
            if cat_escolhida:
                partes_titulo.append(cat_escolhida)
            if subcat_escolhida and subcat_escolhida != "N/A":
                partes_titulo.append(subcat_escolhida)
            if marcas_escolhidas:
                partes_titulo.append(" | ".join(marcas_escolhidas))

            titulo_graf = " + ".join(partes_titulo)
            subtitulo = f"Especificação: {especificacao_extra}" if especificacao_extra else ""

            for loja in sorted(df_agrupado_drill["Loja"].unique()):
                df_loja = df_agrupado_drill[df_agrupado_drill["Loja"] == loja]
                if df_loja.empty:
                    continue

                fig_drill = px.line(
                    df_loja,
                    x="DataCaptura",
                    y="Preco",
                    color="Legenda",
                    markers=True,
                    text="Preco_Label",
                    title=f"{loja.upper()} | {titulo_graf} {subtitulo}",
                    labels={"DataCaptura": "Data da Extração", "Preco": "Preço Médio (R$)", "Legenda": "Item"},
                )
                fig_drill.update_traces(
                    textposition="top center",
                    hovertemplate="<b>Item:</b> %{data.name}<br><b>Data da Extração:</b> %{x|%d/%m/%Y}<br><b>Média:</b> R$ %{y:,.2f}<extra></extra>",
                )
                st.plotly_chart(configurar_grafico_preco(fig_drill, df_loja), use_container_width=True)

            with st.expander("Ver histórico detalhado de preços (Últimos 7 dias)"):
                df_tabela = df_drill.copy()
                df_tabela["DataCaptura"] = pd.to_datetime(df_tabela["DataCaptura"])
                data_maxima = df_tabela["DataCaptura"].max()
                data_limite = data_maxima - pd.Timedelta(days=7)
                df_7_dias = df_tabela[df_tabela["DataCaptura"] >= data_limite].copy()

                df_7_dias["Data"] = df_7_dias["DataCaptura"].dt.strftime("%d/%m/%Y")
                df_7_dias["Preço Real"] = df_7_dias["Preco"].apply(formatar_moeda)

                st.dataframe(
                    df_7_dias.sort_values(["Produto", "DataCaptura"], ascending=[True, False])[
                        ["Data", "Loja", "Marca", "Produto", "Preço Real"]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

    return


# ================= PÁGINA 2: PREVISÃO DE IA =================
def pagina_sistema_predicao():
    conteudo_col, filtros_col = st.columns([4.4, 1.25], gap="large")

    with conteudo_col:
        st.title("Motor Preditivo")
        st.markdown("Utilize Inteligência Artificial para simular cenários de mercado e prever o volume de vendas futuras.")

    if st.session_state.get("dados_tratados") is None or st.session_state["dados_tratados"].empty:
        with filtros_col:
            iniciar_painel_filtros("Filtros e ações")
            texto_apoio("O motor preditivo precisa da base interna tratada antes de liberar os filtros.")
        with conteudo_col:
            painel_erro("<b>Atenção:</b> O Motor de IA está aguardando os dados.")
            painel_info("Vá até <b>Gestão de Dados</b>, faça o upload do CSV e execute o tratamento para liberar o sistema preditivo.")
            placeholder_grafico("Dados internos tratados são necessários para visualizar a projeção.")
        return

    df_interno = st.session_state["dados_tratados"].copy()
    df_aws = carregar_dados_aws()

    with st.spinner("Sincronizando banco interno com AWS e cruzando câmbio..."):
        if df_interno["Preco"].dtype == "object":
            df_interno["Preco"] = (
                df_interno["Preco"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            )

        df_interno["DataCaptura"] = pd.to_datetime(df_interno["DataCaptura"])
        df_interno["Preco"] = pd.to_numeric(df_interno["Preco"], errors="coerce")
        df_interno["Quantidade"] = pd.to_numeric(df_interno["Quantidade"], errors="coerce")
        df_interno = df_interno.dropna(subset=["Preco", "Quantidade"])

        if not df_aws.empty:
            df_aws_limpo = df_aws.copy()
            df_aws_limpo["DataCaptura"] = pd.to_datetime(df_aws_limpo["DataCaptura"]).dt.normalize()
            df_aws_limpo["Marca"] = df_aws_limpo["Marca"].astype(str).str.upper().str.strip()

            if "Dolar" in df_aws_limpo.columns:
                df_aws_limpo["Dolar"] = pd.to_numeric(df_aws_limpo["Dolar"], errors="coerce")
                df_cotacao = df_aws_limpo[["DataCaptura", "Dolar"]].dropna().drop_duplicates(subset=["DataCaptura"])
            else:
                df_cotacao = pd.DataFrame(columns=["DataCaptura", "Dolar"])

            todos_modelos_ordenados = []
            for cat in mapa_subcategorias:
                for modelo in mapa_subcategorias[cat]:
                    todos_modelos_ordenados.append(modelo.upper())
            todos_modelos_ordenados.sort(key=len, reverse=True)

            def extrair_modelo_curto(nome_longo):
                nome_longo = str(nome_longo).upper()
                for modelo in todos_modelos_ordenados:
                    if modelo in nome_longo:
                        return modelo
                return nome_longo.strip()

            df_aws_limpo["Link_IA"] = df_aws_limpo["Produto"].apply(extrair_modelo_curto)
            df_interno["Link_IA"] = df_interno["Produto"].apply(extrair_modelo_curto)

            df_concorrencia = df_aws_limpo.groupby(["DataCaptura", "Link_IA", "Marca"])["Preco"].mean().reset_index()
            df_concorrencia = df_concorrencia.rename(columns={"Preco": "Preco_Concorrencia"})

            df_ml = pd.merge(df_interno, df_concorrencia, on=["DataCaptura", "Link_IA", "Marca"], how="left")
            df_ml["Preco_Concorrencia"] = df_ml.groupby(["Link_IA", "Marca"])["Preco_Concorrencia"].ffill()
            df_ml["Preco_Concorrencia"] = df_ml["Preco_Concorrencia"].fillna(df_ml["Preco"])

            if not df_cotacao.empty:
                df_ml = pd.merge(df_ml, df_cotacao, on="DataCaptura", how="left")
                df_ml["Dolar"] = df_ml["Dolar"].ffill().bfill()
            else:
                df_ml["Dolar"] = 5.00
        else:
            df_ml = df_interno.copy()
            df_ml["Preco_Concorrencia"] = df_ml["Preco"]
            df_ml["Dolar"] = 5.00

        df_ml["Ano"] = df_ml["DataCaptura"].dt.year
        df_ml["Mes"] = df_ml["DataCaptura"].dt.month
        df_ml["DiaDaSemana"] = df_ml["DataCaptura"].dt.dayofweek

    produtos_disponiveis = sorted(df_ml["Produto"].dropna().unique())

    if len(produtos_disponiveis) == 0:
        with filtros_col:
            iniciar_painel_filtros("Filtros e ações")
            texto_apoio("A base tratada não possui produtos válidos para seleção.")
        with conteudo_col:
            painel_erro("<b>Atenção:</b> nenhum produto válido foi encontrado na base tratada.")
            placeholder_grafico("Revise a base em Gestão de Dados para liberar a simulação.")
        return

    with filtros_col:
        iniciar_painel_filtros("Filtros e cenário")
        texto_apoio("Selecione o ativo e ajuste o cenário futuro para processar a previsão.")

        produto_ia = st.selectbox("Hardware Alvo", produtos_disponiveis, key="ia_produto")
        marcas_disponiveis = sorted(df_ml[df_ml["Produto"] == produto_ia]["Marca"].dropna().unique())
        marca_ia = st.selectbox("Fabricante", marcas_disponiveis, key="ia_marca")

        df_alvo = df_ml[(df_ml["Produto"] == produto_ia) & (df_ml["Marca"] == marca_ia)].copy()

        st.markdown('<div class="filter-separator"></div>', unsafe_allow_html=True)
        titulo_secao_filtro("Cenário futuro")

        import datetime
        hoje = datetime.datetime.now()
        ano_atual = hoje.year
        mes_atual_idx = hoje.month - 1

        ano_selecionado = st.selectbox("Ano da Projeção", [ano_atual, ano_atual + 1, ano_atual + 2], key="ia_ano")
        meses_nomes_lista = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
        ]
        meses_opcoes = meses_nomes_lista[mes_atual_idx:] if ano_selecionado == ano_atual else meses_nomes_lista
        mes_selecionado_nome = st.selectbox("Mês da Projeção", meses_opcoes, key="ia_mes")
        mes_alvo_num = meses_nomes_lista.index(mes_selecionado_nome) + 1

        if not df_alvo.empty and "Dolar" in df_alvo.columns and not df_alvo["Dolar"].isna().all():
            dolar_recente = df_alvo.sort_values("DataCaptura", ascending=False)["Dolar"].iloc[0]
        else:
            dolar_recente = 5.00

        try:
            df_nosso_recente = df_interno[
                (df_interno["Produto"].str.contains(produto_ia, case=False)) & (df_interno["Marca"] == marca_ia)
            ]
            preco_recente_nosso = (
                df_nosso_recente.sort_values("DataCaptura", ascending=False)["Preco"].iloc[0]
                if not df_nosso_recente.empty
                else df_alvo.sort_values("DataCaptura", ascending=False)["Preco"].iloc[0]
            )
        except Exception:
            preco_recente_nosso = 0.0

        try:
            df_conc_recente = df_aws[
                (df_aws["Produto"].str.contains(produto_ia, case=False)) & (df_aws["Marca"] == marca_ia)
            ]
            preco_recente_conc = (
                df_conc_recente.sort_values("DataCaptura", ascending=False)["Preco"].iloc[0]
                if not df_conc_recente.empty
                else df_alvo.sort_values("DataCaptura", ascending=False)["Preco_Concorrencia"].iloc[0]
            )
        except Exception:
            preco_recente_conc = 0.0

        preco_simulado = st.number_input("Seu Preço (R$)", value=float(preco_recente_nosso), step=50.0, key="ia_preco")
        preco_conc_simulado = st.number_input("Preço Concorrência (R$)", value=float(preco_recente_conc), step=50.0, key="ia_preco_conc")
        dolar_simulado = st.number_input("Cotação do Dólar (R$)", value=float(dolar_recente), step=0.10, key="ia_dolar")

        processar_ia = st.button(
            "Iniciar IA",
            type="primary",
            width="stretch",
            disabled=len(df_alvo) < 10,
            key="ia_processar",
        )

    if processar_ia and len(df_alvo) >= 10:
        with st.spinner(f"O algoritmo está processando o cenário para {mes_selecionado_nome}/{ano_selecionado}..."):
            time.sleep(1)
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

            X = df_alvo[["Ano", "Mes", "DiaDaSemana", "Preco", "Preco_Concorrencia", "Dolar"]]
            y = df_alvo["Quantidade"]

            X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2, random_state=42)

            modelo_ia = RandomForestRegressor(n_estimators=100, random_state=42)
            modelo_ia.fit(X_treino, y_treino)

            previsoes_teste = modelo_ia.predict(X_teste)
            acuracia_r2 = r2_score(y_teste, previsoes_teste)
            erro_mae = mean_absolute_error(y_teste, previsoes_teste)
            erro_rmse = np.sqrt(mean_squared_error(y_teste, previsoes_teste))

            st.session_state["ultima_acuracia"] = acuracia_r2
            st.session_state["ultima_mae"] = erro_mae
            st.session_state["ultima_rmse"] = erro_rmse
            st.session_state["ultima_importancia"] = modelo_ia.feature_importances_

            X_futuro = pd.DataFrame({
                "Ano": [ano_selecionado],
                "Mes": [mes_alvo_num],
                "DiaDaSemana": [4],
                "Preco": [preco_simulado],
                "Preco_Concorrencia": [preco_conc_simulado],
                "Dolar": [dolar_simulado],
            })

            previsao_ia = modelo_ia.predict(X_futuro)[0]
            previsao_arredondada = max(1, int(previsao_ia))
            faturamento_estimado = previsao_arredondada * preco_simulado

            df_historico_mes = df_alvo[df_alvo["Mes"] == mes_alvo_num]
            media_historica_mes = int(df_historico_mes["Quantidade"].mean()) if not df_historico_mes.empty else "N/A (Sem dados)"

            st.session_state["resultado_simulacao"] = {
                "produto_alvo": produto_ia,
                "marca_alvo": marca_ia,
                "previsao": previsao_arredondada,
                "faturamento": faturamento_estimado,
                "media_historica": media_historica_mes,
                "mes_nome": mes_selecionado_nome,
            }

    with conteudo_col:
        st.markdown("### Ativo selecionado")

        if len(df_alvo) < 10:
            painel_erro(
                f"<b>Atenção:</b> Dados insuficientes para '{produto_ia}' ({marca_ia}). "
                "São necessários pelo menos 10 dias de histórico."
            )
            placeholder_grafico("Selecione um ativo com histórico suficiente para visualizar a projeção.")
            return

        painel_sucesso(f"<b>Base de conhecimento pronta:</b> {len(df_alvo)} registros encontrados para este produto.")

        tab_simulacao, tab_tecnica = st.tabs(["Painel de Simulação", "Painel estatístico"])

        with tab_simulacao:
            st.markdown("### Resultado da Projeção de Demanda")
            resultado = st.session_state.get("resultado_simulacao")
            resultado_valido = (
                resultado is not None
                and resultado.get("produto_alvo") == produto_ia
                and resultado.get("marca_alvo") == marca_ia
            )

            if not resultado_valido:
                placeholder_grafico("Configure o cenário no painel de filtros e clique em Iniciar IA para gerar a projeção.")
            else:
                col_a, col_b, col_c = st.columns(3)
                with col_b:
                    st.metric("Previsão Principal", f"{resultado['previsao']} unid.", delta="Volume esperado", delta_color="off")
                with col_a:
                    st.metric("Cenário Pessimista", f"{int(resultado['previsao'] * 0.85)} unid.", delta="-15% risco", delta_color="inverse")
                with col_c:
                    st.metric("Cenário Otimista", f"{int(resultado['previsao'] * 1.15)} unid.", delta="+15% conversão", delta_color="normal")

                painel_info(
                    f"<h4 style='margin-top:0;color:#94B3FD;'>Projeção Financeira</h4>"
                    f"<p><b>Faturamento Bruto Esperado:</b> {formatar_moeda(resultado['faturamento'])} "
                    f"<i>(baseado no preço sugerido)</i></p>"
                    f"<p style='margin-bottom:0;'><b>Média de Vendas Histórica ({resultado['mes_nome']}):</b> "
                    f"{resultado['media_historica']} unid. <i>(o que costumava vender nesta época)</i></p>"
                )

        with tab_tecnica:
            st.markdown("### Métricas de Validação Científica")
            if "ultima_acuracia" not in st.session_state:
                placeholder_grafico("Execute uma simulação para gerar os dados técnicos.")
            else:
                acuracia = st.session_state["ultima_acuracia"]
                mae = st.session_state["ultima_mae"]
                rmse = st.session_state["ultima_rmse"]
                importancias = st.session_state["ultima_importancia"]

                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.metric("Score de Tendência (R²)", f"{acuracia * 100:.1f}%")
                with col_m2:
                    st.metric("Erro Médio Absoluto (MAE)", f"{mae:.1f} unid.")
                with col_m3:
                    st.metric("Erro Quadrático (RMSE)", f"{rmse:.1f} unid.")

                if acuracia > 0.80:
                    painel_sucesso("Grau de confiança <b>Excepcional</b>. O modelo prevê a tendência com alta precisão.")
                elif acuracia > 0.60:
                    painel_info("Grau de confiança <b>Bom</b>. O modelo compreende a dinâmica do mercado.")
                else:
                    painel_erro("Grau de confiança <b>Baixo</b>. O mercado atual está instável ou faltam dados.")

                st.markdown("### Importância das Variáveis")
                df_importancia = pd.DataFrame({
                    "Variável Analisada": [
                        "Ano",
                        "Mês (Sazonalidade)",
                        "Dia da Semana",
                        "Nosso Preço",
                        "Preço Concorrência",
                        "Cotação do Dólar",
                    ],
                    "Peso na Decisão (%)": importancias * 100,
                }).sort_values("Peso na Decisão (%)", ascending=True)

                fig_imp = px.bar(
                    df_importancia,
                    x="Peso na Decisão (%)",
                    y="Variável Analisada",
                    orientation="h",
                    title=f"Matriz de Decisão da IA para: {marca_ia} {produto_ia}",
                )
                fig_imp.update_traces(
                    marker_color="#0066CC",
                    hovertemplate="<b>%{y}</b><br>Peso: %{x:.1f}%<extra></extra>",
                )
                fig_imp.update_layout(
                    showlegend=False,
                    bargap=0.4,
                    height=440,
                    xaxis_title="Peso (%) na Decisão de Compra",
                    yaxis_title=None,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#FFFFFF"),
                    margin=dict(l=20, r=20, t=70, b=40),
                    xaxis=dict(showgrid=True, gridcolor="#333333"),
                )
                st.plotly_chart(fig_imp, use_container_width=True)

    return


# ================= GESTÃO DE DADOS =================
def pagina_gestao_dados():
    if "dados_brutos" not in st.session_state:
        st.session_state["dados_brutos"] = None
    if "dados_tratados" not in st.session_state:
        st.session_state["dados_tratados"] = None
    if "linhas_removidas" not in st.session_state:
        st.session_state["linhas_removidas"] = 0
    if "arquivo_upload_nome" not in st.session_state:
        st.session_state["arquivo_upload_nome"] = None

    conteudo_col, filtros_col = st.columns([4.4, 1.25], gap="large")
    mensagem_upload = None
    erro_upload = None

    with filtros_col:
        iniciar_painel_filtros("Dados e ações")
        texto_apoio("Use este painel para carregar o CSV, tratar os dados e liberar o motor preditivo.")
        arquivo_upload = st.file_uploader("CSV de vendas internas", type=["csv"], key="dados_upload")

        executar_tratamento = st.button(
            "Executar Tratamento",
            type="primary",
            width="stretch",
            disabled=st.session_state["dados_brutos"] is None,
            key="dados_executar_tratamento",
        )

        limpar_memoria = st.button(
            "Limpar e subir novo",
            width="stretch",
            disabled=st.session_state["dados_brutos"] is None and st.session_state["dados_tratados"] is None,
            key="dados_limpar_memoria",
        )

    if limpar_memoria:
        st.session_state["dados_brutos"] = None
        st.session_state["dados_tratados"] = None
        st.session_state["linhas_removidas"] = 0
        st.session_state["arquivo_upload_nome"] = None
        st.rerun()

    if arquivo_upload is not None and st.session_state["arquivo_upload_nome"] != arquivo_upload.name:
        try:
            df_teste = pd.read_csv(arquivo_upload)
            colunas_obrigatorias = ["DataCaptura", "Marca", "Produto", "Descricao", "Preco", "Quantidade"]
            colunas_ausentes = [col for col in colunas_obrigatorias if col not in df_teste.columns]

            if len(colunas_ausentes) > 0:
                erro_upload = (
                    "<b>Erro de Formatação:</b> faltam as seguintes colunas no CSV: "
                    + ", ".join(colunas_ausentes)
                )
            else:
                st.session_state["dados_brutos"] = df_teste
                st.session_state["dados_tratados"] = None
                st.session_state["arquivo_upload_nome"] = arquivo_upload.name
                mensagem_upload = "<b>Ficheiro validado e carregado com sucesso.</b>"
        except Exception as e:
            erro_upload = f"<b>Erro ao ler o ficheiro:</b> {e}"

    if executar_tratamento and st.session_state["dados_brutos"] is not None:
        with st.spinner("Aplicando algoritmos de normalização..."):
            time.sleep(1)

            df_tratado = st.session_state["dados_brutos"].copy()
            tamanho_original = len(df_tratado)

            df_tratado.columns = df_tratado.columns.str.strip()
            df_tratado = df_tratado.dropna(how="all")
            df_tratado = df_tratado.loc[:, ~df_tratado.columns.str.contains("^Unnamed")]

            colunas_texto = ["Marca", "Produto", "Descricao"]
            for col in colunas_texto:
                if col in df_tratado.columns:
                    df_tratado[col] = df_tratado[col].astype(str).str.upper().str.strip()
                    if col == "Produto":
                        df_tratado["Produto"] = df_tratado["Produto"].apply(lambda x: re.sub(r"^[\d\s-]+\s*", "", str(x)))
                        df_tratado["Produto"] = df_tratado["Produto"].str.strip()

            if "Preco" in df_tratado.columns:
                def limpar_moeda_inteligente(valor):
                    if pd.isna(valor):
                        return valor
                    valor_limpo = str(valor).replace("R$", "").replace(" ", "").strip()
                    if "," in valor_limpo:
                        valor_limpo = valor_limpo.replace(".", "").replace(",", ".")
                    return valor_limpo

                df_tratado["Preco"] = df_tratado["Preco"].apply(limpar_moeda_inteligente)
                df_tratado["Preco"] = pd.to_numeric(df_tratado["Preco"], errors="coerce")
                df_tratado = df_tratado.dropna(subset=["Preco"])

            if "Quantidade" in df_tratado.columns:
                df_tratado["Quantidade"] = pd.to_numeric(df_tratado["Quantidade"], errors="coerce").fillna(0).astype(int)
                df_tratado = df_tratado[df_tratado["Quantidade"] > 0]

            if "DataCaptura" in df_tratado.columns:
                df_tratado["DataCaptura"] = pd.to_datetime(df_tratado["DataCaptura"], errors="coerce", dayfirst=True)
                df_tratado = df_tratado.dropna(subset=["DataCaptura"])
                df_tratado["DataCaptura"] = df_tratado["DataCaptura"].dt.strftime("%Y-%m-%d")

            st.session_state["dados_tratados"] = df_tratado
            st.session_state["linhas_removidas"] = tamanho_original - len(df_tratado)

    with conteudo_col:
        st.title("Ingestão, Limpeza e Tratamento")
        st.write("Carregamento e padronização do histórico de vendas.")

        st.markdown("### Padrão Exigido para o CSV")
        painel_info(
            "Para o modelo de Inteligência Artificial cruzar seu histórico de vendas com os preços da concorrência, "
            "o CSV deve ter exatamente estas colunas: <br>"
            "<b>DataCaptura</b>, <b>Marca</b>, <b>Produto</b>, <b>Descricao</b>, <b>Preco</b> e <b>Quantidade</b>."
        )

        if erro_upload:
            painel_erro(erro_upload)
        elif mensagem_upload:
            painel_sucesso(mensagem_upload)

        if st.session_state["dados_brutos"] is None:
            placeholder_grafico("Suba um CSV no painel de filtros para visualizar e tratar os dados.")
        else:
            st.markdown("### Dados recebidos")
            st.dataframe(st.session_state["dados_brutos"], use_container_width=True)

            if st.session_state["dados_tratados"] is None:
                placeholder_grafico("Clique em Executar Tratamento no painel lateral para normalizar a base.")
            else:
                st.markdown("### Dados Normalizados e Prontos")
                st.dataframe(st.session_state["dados_tratados"], use_container_width=True)
                painel_sucesso(
                    f"<b>Operação concluída!</b> {st.session_state['linhas_removidas']} linhas de lixo ou nulas removidas. "
                    "Valores formatados para a IA e datas alinhadas com o banco AWS."
                )

    return


paginas_app = [
    st.Page(pagina_pesquisa_mercado, title="Pesquisa de Mercado", url_path="", default=True),
    st.Page(pagina_sistema_predicao, title="Sistema de predição", url_path="predicao"),
    st.Page(pagina_gestao_dados, title="Gestão de Dados", url_path="dados"),
]

pagina_atual = st.navigation(paginas_app, position="hidden")
renderizar_menu_superior(pagina_atual, paginas_app)
pagina_atual.run()
