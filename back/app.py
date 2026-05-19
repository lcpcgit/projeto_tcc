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

# ================= CONFIGURAÇÃO VISUAL DE DESIGN (QUASE PRETO + VERMELHO + AZUL) =================
st.markdown("""
<style>
    /* 1. Força o fundo do aplicativo inteiro para Quase Preto (#121212) */
    .stApp {
        background-color: #121212 !important;
        color: #FFFFFF !important;
    }

    /* Pinta a barra superior (Header) da mesma cor do fundo para ficar perfeitamente integrada */
    header[data-testid="stHeader"] {
        background-color: #121212 !important;
    }
    
    /* ATUALIZADO: Pinta o menu lateral (Sidebar) com o mesmo Azul Tecnológico das caixas */
    section[data-testid="stSidebar"] {
        background-color: #0D2137 !important;
    }

    /* 2. Customiza os botões principais para Vermelho Escuro / Gamer */
    div.stButton > button {
        background-color: #8B0000 !important;
        color: #FFFFFF !important;
        border: 1px solid #FF0000 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        background-color: #FF0000 !important;
        border: 1px solid #FF4B4B !important;
        box-shadow: 0px 0px 10px #FF0000 !important;
    }

    /* 3. Transforma todas as caixas de informação (st.info nativas, se houver) no Azul Tecnológico */
    .stAlert {
        background-color: #0D2137 !important;
        color: #94B3FD !important;
        border-left: 5px solid #0066CC !important;
        border-radius: 8px !important;
    }

    /* 4. Alinha as Abas (Tabs) para combinarem com o tema vermelho */
    button[data-baseweb="tab"] {
        color: #CCCCCC !important;
    }
    button[aria-selected="true"] {
        color: #FF4B4B !important;
        border-bottom-color: #FF4B4B !important;
    }

    /* Ajusta inputs e selectboxes para não sumirem no fundo escuro */
    div[data-baseweb="select"] > div {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
    }
    input {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
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

# ================= MENU LATERAL =================
st.sidebar.title("Menu")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegação do Sistema:",
    ["Pesquisa de Mercado", 
     "Sistema de predição", 
     "Gestão de Dados"]
)

# ================= DASHBOARD =================
if menu == "Pesquisa de Mercado":
    st.title("Scanner")
    st.write("Acompanhe o histórico de preços praticados pelas maiores lojas de hardware do Brasil (Kabum e Terabyte).")
    
    df_historico = carregar_dados_aws()
    
    if not df_historico.empty:
        st.write("Tendência de Preços")
        
        modo_visao = st.radio(
            "Selecione o Nível de Análise:", 
            ["Visão Geral", "Visão Específica"],
            horizontal=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True) 
        
        if modo_visao == "Visão Geral":
            st.markdown("""
            <div style="background-color: #0D2137; padding: 15px; border-radius: 8px; border-left: 5px solid #0066CC; color: #94B3FD; margin-bottom: 15px;">
                 Digite a família da peça (Ex: RTX 5070 RX 7600) e o sistema devolverá a média de preços de todos os modelos daquela linha.
            </div>
            """, unsafe_allow_html=True)
            
            if 'ultima_busca' not in st.session_state:
                st.session_state['ultima_busca'] = "rtx 5070" 
                
            familia_input = st.text_input("Digite a Família do Hardware:", value=st.session_state['ultima_busca'])
            
            st.session_state['ultima_busca'] = familia_input
            
            if familia_input:
                def limpar_texto_busca(texto):
                    if not isinstance(texto, str): return ""
                    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
                    texto = texto.lower().strip()
                    texto = re.sub(r'[^\w\s]', ' ', texto)
                    texto = re.sub(r'\s+', ' ', texto)
                    return texto

                busca_limpa = limpar_texto_busca(familia_input)
                palavras_busca = busca_limpa.split()
                df_historico['ProdutoLimpo'] = df_historico['Produto'].apply(limpar_texto_busca)

                def aplicar_filtro_exclusivo(nome_do_produto, palavras_da_pesquisa):
                    if 'mouse' in palavras_da_pesquisa and 'gamer' not in palavras_da_pesquisa:
                        return 'mouse' in nome_do_produto and 'gamer' not in nome_do_produto
                    return all(palavra in nome_do_produto for palavra in palavras_da_pesquisa)

                mascara_filtro = df_historico['ProdutoLimpo'].apply(lambda nome: aplicar_filtro_exclusivo(nome, palavras_busca))
                df_filtrado = df_historico[mascara_filtro].copy()
                df_historico = df_historico.drop(columns=['ProdutoLimpo'])

                if not df_filtrado.empty:
                    df_agrupado = df_filtrado.groupby(['DataCaptura', 'Loja'])['Preco'].mean().reset_index()
                    df_agrupado['Preco_Label'] = df_agrupado['Preco'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    
                    fig = px.line(df_agrupado, x="DataCaptura", y="Preco", color="Loja", markers=True, text="Preco_Label", title=f"Média de Mercado da Família: {familia_input.upper()}", labels={"DataCaptura": "Data", "Preco": "Preço (R$)", "Loja": "Loja"})
                    
                    fig.update_traces(
                        textposition="top center",
                        hovertemplate="<b>Loja:</b> %{data.name}<br><b>Data da Extração:</b> %{x|%d/%m/%Y}<br><b>Média:</b> R$ %{y:,.2f}<extra></extra>"
                    )
                    
                    fig.update_layout(
                        yaxis=dict(range=[df_agrupado['Preco'].min() * 0.9, df_agrupado['Preco'].max() * 1.1]),
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#FFFFFF'),
                        xaxis=dict(showgrid=True, gridcolor='#333333'),
                        yaxis_title="Preço (R$)"
                    ) 
                    fig.update_xaxes(tickformat="%d/%m/%Y", showgrid=True, gridcolor='#333333')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: #330000; padding: 15px; border-radius: 8px; border-left: 5px solid #FF0000; color: #FFF;">
                         <b>Atenção:</b> Sem dados históricos para a família '{familia_input}'.
                    </div><br>
                    """, unsafe_allow_html=True)
                    
        elif modo_visao == "Visão Específica":
            st.markdown("""
            <div style="background-color: #0D2137; padding: 15px; border-radius: 8px; border-left: 5px solid #0066CC; color: #94B3FD; margin-bottom: 15px;">
                 Selecione o modelo exato para analisar o preço dele.
            </div>
            """, unsafe_allow_html=True)
            
            pesquisa_produto = st.text_input("Filtre pela família/marca do produto:", key="input_pesquisa_especifica")
            if pesquisa_produto:
                termos_busca = pesquisa_produto.lower().split()
                mask = pd.Series(True, index=df_historico.index)
                
                for termo in termos_busca:
                    mask = mask & df_historico['Produto'].str.lower().str.contains(termo, na=False, regex=False)
                
                if "ti" not in termos_busca:
                    mask = mask & ~df_historico['Produto'].str.lower().str.contains(r'(?<![a-z])ti(?![a-z])', regex=True, na=False)
                
                if "super" not in termos_busca:
                    mask = mask & ~df_historico['Produto'].str.lower().str.contains(r'(?<![a-z])super(?![a-z])', regex=True, na=False)
                    
                if "xt" not in termos_busca:
                    mask = mask & ~df_historico['Produto'].str.lower().str.contains(r'(?<![a-z])xt(?![a-z])', regex=True, na=False)
                
                lista_filtrada = df_historico[mask]['Produto'].astype(str).str.strip().dropna().unique()
                lista_filtrada = sorted(lista_filtrada)
                
                if len(lista_filtrada) == 0:
                    lista_filtrada = ["Nenhum produto encontrado com esses termos."]
            else:
                lista_filtrada = ["Digite algo na pesquisa acima para encontrar o produto"]
                
            esta_bloqueado = len(lista_filtrada) == 1 and (lista_filtrada[0].startswith("Digite algo") or lista_filtrada[0].startswith("Nenhum produto"))
            
            produto_escolhido = st.selectbox(
                "Escolha o Hardware específico:", 
                lista_filtrada,
                disabled=esta_bloqueado,
                key="select_produto_especifico"
            )
            
            if produto_escolhido and not esta_bloqueado:
                df_filtrado = df_historico[df_historico['Produto'].astype(str).str.strip() == produto_escolhido].copy()
                
                if not df_filtrado.empty:
                    df_filtrado['Preco_Label'] = df_filtrado['Preco'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    
                    fig = px.line(
                        df_filtrado, 
                        x="DataCaptura", 
                        y="Preco", 
                        color="Loja", 
                        markers=True, 
                        text="Preco_Label",
                        title=f"Histórico Específico: {produto_escolhido}",
                        labels={"DataCaptura": "Data da Extração", "Preco": "Preço à Vista (R$)", "Loja": "Loja Monitorada"}
                    )
                    
                    fig.update_traces(
                        textposition="top center",
                        hovertemplate="<b>Loja:</b> %{data.name}<br><b>Data da Extração:</b> %{x|%d/%m/%Y}<br><b>Preço:</b> R$ %{y:,.2f}<extra></extra>"
                    )
                    
                    fig.update_layout(
                        yaxis=dict(range=[df_filtrado['Preco'].min() * 0.9, df_filtrado['Preco'].max() * 1.1]),
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#FFFFFF'),
                        xaxis=dict(showgrid=True, gridcolor='#333333'),
                        yaxis_title="Preço (R$)"
                    )
                    fig.update_xaxes(tickformat="%d/%m/%Y", showgrid=True, gridcolor='#333333')
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.markdown("""
                    <div style="background-color: #330000; padding: 15px; border-radius: 8px; border-left: 5px solid #FF0000; color: #FFF;">
                        ⚠️ <b>Atenção:</b> Sem dados suficientes para gerar o gráfico deste produto específico.
                    </div><br>
                    """, unsafe_allow_html=True)
            else:
                 st.markdown("""
                 <div style="background-color: #0D2137; padding: 15px; border-radius: 8px; border-left: 5px solid #0066CC; color: #94B3FD; margin-top: 15px;">
                      Por favor, pesquise e selecione um produto na lista acima.
                 </div>
                 """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.write("Análise De Filtros Avançados")
        st.write("Filtre o mercado através de categorias, modelos, marcas e especificações.")

        todos_os_modelos = sorted(list(set(sum(mapa_subcategorias.values(), []))))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cat_escolhida = st.selectbox("1. Categoria:", [""] + sorted(categorias_base))
            
        if cat_escolhida:
            modelos_da_cat = mapa_subcategorias.get(cat_escolhida, [])
            if len(modelos_da_cat) > 0:
                opcoes_modelo = [""] + sorted(modelos_da_cat)
                disabled_mod = False
            else:
                opcoes_modelo = ["N/A"]
                disabled_mod = True
        else:
            opcoes_modelo = [""] + todos_os_modelos
            disabled_mod = False
            
        with col2:
            subcat_escolhida = st.selectbox("2. Modelo:", opcoes_modelo, disabled=disabled_mod)

        df_drill = df_historico.copy()
        
        if cat_escolhida:
            termo_cat_limpo = ''.join(c for c in unicodedata.normalize('NFD', cat_escolhida) if unicodedata.category(c) != 'Mn').lower()
            
            if termo_cat_limpo == "placa de video":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('video|vídeo|vga|geforce|radeon|rtx|gtx|rx|arc|gpu', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('placa mae|placa-mae|cooler|water|espelho|suporte|cabo|fonte|mouse|teclado|monitor|headset|cadeira|mesa|ssd|hd ', na=False)]
                
            elif termo_cat_limpo == "processador":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('processador|ryzen|core i|athlon|celeron|pentium', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('placa|cooler|water|fan|gabinete|memoria|notebook|pc|computador|desktop|mouse|teclado|monitor|headset|fonte|ssd|hd |gpu', na=False)]
                
            elif termo_cat_limpo == "placa mae":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('placa|motherboard|mainboard', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('video|vídeo|cooler|mouse|teclado|monitor|headset|fonte|processador|gpu', na=False)]
                
            elif termo_cat_limpo == "memoria ram":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('memoria|ram|ddr', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('placa|video|vídeo|cooler|mouse|teclado|monitor|headset|fonte|processador|gpu|gddr', na=False)]
                
            elif "fonte" in termo_cat_limpo:
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('fonte|atx|power', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('cabo|adaptador|placa|video|cooler|mouse|teclado|monitor|headset|processador|memoria', na=False)]
                
            elif termo_cat_limpo == "monitor":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('monitor|tela|display', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('cabo|hdmi|adaptador|suporte|braco|braço|pistao|pistão|tv|televisao|televisão|placa', na=False)]
            
            elif termo_cat_limpo == "ssd":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('ssd|nvme|m\.2|sata', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains(r'cabo|adaptador|dissipador|heatsink|case|gaveta|placa|cooler|\bhd\b|disco rigido|hard drive', na=False, regex=True)]
                
            elif termo_cat_limpo == "hd":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('hd |disco rigido|hard drive|hd externo', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('ssd|cabo|adaptador|gaveta|case|monitor|tv|placa', na=False)]

            elif termo_cat_limpo == "water cooler":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('water cooler|watercooler|liquid cooler', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('gabinete|placa|processador|fan|ventoinha|ar', na=False)]

            elif termo_cat_limpo == "air cooler":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('air cooler|aircooler|cooler para processador', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('water|liquido|gabinete|fan |ventoinha', na=False)]

            elif termo_cat_limpo == "fan":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('fan|ventoinha|cooler para gabinete', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('water|air|processador|gabinete|placa', na=False)]

            elif termo_cat_limpo == "gabinete":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('gabinete|case', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('cooler|fan|ventoinha|placa|fonte|memoria', na=False)]

            elif termo_cat_limpo == "headset gamer":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('headset|fone', na=False) & df_drill['Produto'].str.lower().str.contains('gamer', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('suporte|mouse|teclado|cadeira|mesa', na=False)]

            elif termo_cat_limpo == "mouse":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('mouse', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('gamer|mousepad|pad|teclado|headset|monitor|placa|cooler|fonte|memoria|processador', na=False)]
                
            elif termo_cat_limpo == "mouse gamer":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('mouse', na=False) & df_drill['Produto'].str.lower().str.contains('gamer', na=False)]
                df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('mousepad|pad|teclado|headset|monitor|placa|cooler|fonte|memoria|processador', na=False)]
                
            elif termo_cat_limpo == "teclado mecanico":
                 df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('teclado', na=False) & df_drill['Produto'].str.lower().str.contains('mecanico|mecânico', na=False)]
                 df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('mouse|kit|combo', na=False)]
                 
            elif termo_cat_limpo == "teclado magnetico":
                 df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('teclado', na=False) & df_drill['Produto'].str.lower().str.contains('magnetico|magnético', na=False)]
                 df_drill = df_drill[~df_drill['Produto'].str.lower().str.contains('mouse|kit|combo', na=False)]
                 
            else:
                 for palavra in termo_cat_limpo.split():
                     df_drill = df_drill[df_drill['Produto'].str.lower().str.contains(palavra, na=False)]
                     
        if subcat_escolhida and subcat_escolhida != "N/A":
            mask = pd.Series(True, index=df_drill.index)
            partes_busca = subcat_escolhida.lower().split()
            
            for p in partes_busca:
                padrao_parte = r'\b' + re.escape(p) + r'\b'
                
                if p.isdigit():
                    padrao_parte = re.escape(p) 
                elif p.endswith('tb') or p.endswith('gb'):
                    padrao_parte = r'(?<![a-z0-9])' + re.escape(p) + r'(?![a-z0-9])'
                
                mask = mask & df_drill['Produto'].str.lower().str.contains(padrao_parte, regex=True, na=False)
            
            modelos_derivados = []
            lista_para_verificar = mapa_subcategorias.get(cat_escolhida, todos_os_modelos) if cat_escolhida else todos_os_modelos
                
            for modelo in lista_para_verificar:
                if modelo != subcat_escolhida and subcat_escolhida.lower() in modelo.lower():
                    modelos_derivados.append(modelo)
                    
            for derivado in modelos_derivados:
                mask_derivado = pd.Series(True, index=df_drill.index)
                for p in derivado.lower().split():
                    padrao_parte_excl = r'\b' + re.escape(p) + r'\b'
                    if p.isdigit():
                        padrao_parte_excl = re.escape(p)
                    elif p.endswith('tb') or p.endswith('gb'):
                        padrao_parte_excl = r'(?<![a-z0-9])' + re.escape(p) + r'(?![a-z0-9])'
                        
                    mask_derivado = mask_derivado & df_drill['Produto'].str.lower().str.contains(padrao_parte_excl, regex=True, na=False)
                
                mask = mask & ~mask_derivado
                
            df_drill = df_drill[mask]

        marcas_validas = sorted([m for m in df_drill['Marca'].dropna().unique()])
        
        with col3:
            marcas_escolhidas = st.multiselect("3. Marcas:", marcas_validas)
            
        if len(marcas_escolhidas) > 0:
            df_drill = df_drill[df_drill['Marca'].isin(marcas_escolhidas)]

        with col4:
            especificacao_extra = st.text_input("4. Especificação (Ex: Branco, OC):")
            
        if especificacao_extra:
            espec_limpa = ''.join(c for c in unicodedata.normalize('NFD', especificacao_extra) if unicodedata.category(c) != 'Mn').lower()
            df_drill = df_drill[df_drill['Produto'].str.lower().str.contains(espec_limpa, na=False)]

        filtros_ativos = 0
        if cat_escolhida: filtros_ativos += 1
        if subcat_escolhida and subcat_escolhida != "N/A": filtros_ativos += 1
        if len(marcas_escolhidas) > 0: filtros_ativos += 1
        if especificacao_extra: filtros_ativos += 1

        if filtros_ativos < 2:
            st.markdown("""
            <div style="background-color: #0D2137; padding: 15px; border-radius: 8px; border-left: 5px solid #0066CC; color: #94B3FD; margin-top: 15px;">
                 Preencha pelo menos DUAS opções (Ex: Categoria + Marca, ou Modelo + Marca) para visualizar o histórico de preços.
            </div>
            """, unsafe_allow_html=True)
        else:
            if not df_drill.empty:
                st.markdown("<br>", unsafe_allow_html=True) 
                col_vazia, col_filtro_preco = st.columns([3, 1]) 
                
                with col_filtro_preco:
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
                            "Acima de R$ 8.000"
                        ]
                    )
                
                if filtro_preco == "Abaixo de R$ 100":
                    df_drill = df_drill[df_drill['Preco'] < 100]
                elif filtro_preco == "R$ 100 a R$ 500":
                    df_drill = df_drill[(df_drill['Preco'] >= 100) & (df_drill['Preco'] <= 500)]
                elif filtro_preco == "R$ 500 a R$ 1.500":
                    df_drill = df_drill[(df_drill['Preco'] > 500) & (df_drill['Preco'] <= 1500)]
                elif filtro_preco == "R$ 1.500 a R$ 3.000":
                    df_drill = df_drill[(df_drill['Preco'] > 1500) & (df_drill['Preco'] <= 3000)]
                elif filtro_preco == "R$ 3.000 a R$ 5.000":
                    df_drill = df_drill[(df_drill['Preco'] > 3000) & (df_drill['Preco'] <= 5000)]
                elif filtro_preco == "R$ 5.000 a R$ 8.000":
                    df_drill = df_drill[(df_drill['Preco'] > 5000) & (df_drill['Preco'] <= 8000)]
                elif filtro_preco == "Acima de R$ 8.000":
                    df_drill = df_drill[df_drill['Preco'] > 8000]

                if not df_drill.empty:
                    if subcat_escolhida != "" and subcat_escolhida != "N/A":
                        df_agrupado_drill = df_drill.groupby(['DataCaptura', 'Loja', 'Marca'])['Preco'].mean().reset_index()
                        df_agrupado_drill['Legenda'] = df_agrupado_drill['Marca'] 
                    else:
                        df_agrupado_drill = df_drill.groupby(['DataCaptura', 'Loja', 'Produto'])['Preco'].mean().reset_index()
                        df_agrupado_drill['Produto_Curto'] = df_agrupado_drill['Produto'].apply(lambda x: x[:40] + "..." if len(x) > 40 else x)
                        df_agrupado_drill['Legenda'] = df_agrupado_drill['Produto_Curto']
                    
                    df_agrupado_drill['Preco_Label'] = df_agrupado_drill['Preco'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    
                    partes_titulo = []
                    if cat_escolhida: partes_titulo.append(cat_escolhida)
                    if subcat_escolhida and subcat_escolhida != "N/A": partes_titulo.append(subcat_escolhida)
                    if marcas_escolhidas: partes_titulo.append(" | ".join(marcas_escolhidas))
                    
                    titulo_graf = " + ".join(partes_titulo)
                    subtitulo = f"Especificação: {especificacao_extra}" if especificacao_extra else ""
                    
                    lojas_presentes = sorted(df_agrupado_drill['Loja'].unique())
                    
                    for loja in lojas_presentes:
                        df_loja = df_agrupado_drill[df_agrupado_drill['Loja'] == loja]
                        
                        if not df_loja.empty:
                            fig_drill = px.line(
                                df_loja, 
                                x="DataCaptura", 
                                y="Preco", 
                                color="Legenda", 
                                markers=True, 
                                text="Preco_Label", 
                                title=f" {loja.upper()} | {titulo_graf} {subtitulo}", 
                                labels={"DataCaptura": "Data da Extração", "Preco": "Preço Médio (R$)", "Legenda": "Item"}
                            )
                            
                            fig_drill.update_traces(
                                textposition="top center",
                                hovertemplate="<b>Item:</b> %{data.name}<br><b>Data da Extração:</b> %{x|%d/%m/%Y}<br><b>Média:</b> R$ %{y:,.2f}<extra></extra>"
                            )
                            
                            fig_drill.update_layout(
                                yaxis=dict(range=[df_loja['Preco'].min() * 0.9, df_loja['Preco'].max() * 1.1]),
                                paper_bgcolor='rgba(0,0,0,0)', 
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#FFFFFF'),
                                xaxis=dict(showgrid=True, gridcolor='#333333'),
                                yaxis_title="Preço (R$)"
                            )
                            fig_drill.update_xaxes(tickformat="%d/%m/%Y", showgrid=True, gridcolor='#333333')
                            
                            st.plotly_chart(fig_drill, use_container_width=True)
                    
                    with st.expander("Ver histórico detalhado de preços (Últimos 7 dias)"):
                        df_tabela = df_drill.copy()
                        df_tabela['DataCaptura'] = pd.to_datetime(df_tabela['DataCaptura'])
                        data_maxima = df_tabela['DataCaptura'].max()
                        data_limite = data_maxima - pd.Timedelta(days=7)
                        df_7_dias = df_tabela[df_tabela['DataCaptura'] >= data_limite].copy()
                        
                        df_7_dias['Data'] = df_7_dias['DataCaptura'].dt.strftime('%d/%m/%Y')
                        df_7_dias['Preço Real'] = df_7_dias['Preco'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                        
                        st.dataframe(
                            df_7_dias.sort_values(['Produto', 'DataCaptura'], ascending=[True, False])[['Data', 'Loja', 'Marca', 'Produto', 'Preço Real']],
                            width='stretch',
                            hide_index=True
                        )
                else:
                    st.markdown(f"""
                    <div style="background-color: #330000; padding: 15px; border-radius: 8px; border-left: 5px solid #FF0000; color: #FFF;">
                        ⚠️ <b>Atenção:</b> Nenhum produto encontrado na faixa '{filtro_preco}'.
                    </div><br>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #330000; padding: 15px; border-radius: 8px; border-left: 5px solid #FF0000; color: #FFF;">
                    ⚠️ <b>Atenção:</b> Nenhum hardware encontrado no banco de dados com essa combinação exata de filtros.
                </div><br>
                """, unsafe_allow_html=True)

# ================= PÁGINA 2: PREVISÃO DE IA =================
elif menu == "Sistema de predição":
    st.title(" Motor Preditivo")
    st.markdown("Utilize Inteligência Artificial para simular cenários de mercado e prever o volume de vendas futuras.")

    if st.session_state.get('dados_tratados') is None or st.session_state['dados_tratados'].empty:
        st.markdown("""
        <div style="background-color: #330000; padding: 15px; border-radius: 8px; border-left: 5px solid #FF0000; color: #FFF; margin-bottom: 10px;">
             <b>Atenção:</b> O Motor de IA está aguardando os dados.
        </div>
        <div style="background-color: #0D2137; padding: 15px; border-radius: 8px; border-left: 5px solid #0066CC; color: #94B3FD;">
            Vá até a aba <b>'Gestão de Dados'</b>, faça o upload do seu ficheiro CSV e clique em <b>'Executar Tratamento'</b> para liberar o sistema preditivo.
        </div>
        """, unsafe_allow_html=True)
    else:
        df_interno = st.session_state['dados_tratados'].copy()
        df_aws = carregar_dados_aws()

        with st.spinner("Sincronizando banco de dados interno com nuvem AWS e cruzando Câmbio (Dólar)..."):
            
            if df_interno['Preco'].dtype == 'object':
                df_interno['Preco'] = df_interno['Preco'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            
            df_interno['DataCaptura'] = pd.to_datetime(df_interno['DataCaptura'])
            df_interno['Preco'] = pd.to_numeric(df_interno['Preco'], errors='coerce')
            df_interno['Quantidade'] = pd.to_numeric(df_interno['Quantidade'], errors='coerce')
            df_interno = df_interno.dropna(subset=['Preco', 'Quantidade'])

            if not df_aws.empty:
                df_aws_limpo = df_aws.copy()
                df_aws_limpo['DataCaptura'] = pd.to_datetime(df_aws_limpo['DataCaptura']).dt.normalize() 
                df_aws_limpo['Marca'] = df_aws_limpo['Marca'].astype(str).str.upper().str.strip()
                
                if 'Dolar' in df_aws_limpo.columns:
                    df_aws_limpo['Dolar'] = pd.to_numeric(df_aws_limpo['Dolar'], errors='coerce')
                    df_cotacao = df_aws_limpo[['DataCaptura', 'Dolar']].dropna().drop_duplicates(subset=['DataCaptura'])
                else:
                    df_cotacao = pd.DataFrame(columns=['DataCaptura', 'Dolar'])
                
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

                df_aws_limpo['Link_IA'] = df_aws_limpo['Produto'].apply(extrair_modelo_curto)
                df_interno['Link_IA'] = df_interno['Produto'].apply(extrair_modelo_curto)
                
                df_concorrencia = df_aws_limpo.groupby(['DataCaptura', 'Link_IA', 'Marca'])['Preco'].mean().reset_index()
                df_concorrencia = df_concorrencia.rename(columns={'Preco': 'Preco_Concorrencia'})
                
                df_ml = pd.merge(df_interno, df_concorrencia, on=['DataCaptura', 'Link_IA', 'Marca'], how='left')
                df_ml['Preco_Concorrencia'] = df_ml.groupby(['Link_IA', 'Marca'])['Preco_Concorrencia'].ffill()
                df_ml['Preco_Concorrencia'] = df_ml['Preco_Concorrencia'].fillna(df_ml['Preco'])
                
                if not df_cotacao.empty:
                    df_ml = pd.merge(df_ml, df_cotacao, on='DataCaptura', how='left')
                    df_ml['Dolar'] = df_ml['Dolar'].ffill().bfill()
                else:
                    df_ml['Dolar'] = 5.00
            else:
                df_ml = df_interno.copy()
                df_ml['Preco_Concorrencia'] = df_ml['Preco']
                df_ml['Dolar'] = 5.00

            df_ml['Ano'] = df_ml['DataCaptura'].dt.year
            df_ml['Mes'] = df_ml['DataCaptura'].dt.month
            df_ml['DiaDaSemana'] = df_ml['DataCaptura'].dt.dayofweek

        st.markdown("### 1. Seleção de Ativo")
        produtos_disponiveis = sorted(df_ml['Produto'].dropna().unique())
        
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            produto_ia = st.selectbox("Hardware Alvo:", produtos_disponiveis)
        
        marcas_disponiveis = sorted(df_ml[df_ml['Produto'] == produto_ia]['Marca'].dropna().unique())
        with col_sel2:
            marca_ia = st.selectbox("Fabricante:", marcas_disponiveis)
        
        df_alvo = df_ml[(df_ml['Produto'] == produto_ia) & (df_ml['Marca'] == marca_ia)].copy()
        
        if len(df_alvo) < 10:
            st.markdown(f"""
            <div style="background-color: #330000; padding: 15px; border-radius: 8px; border-left: 5px solid #FF0000; color: #FFF;">
                 <b>Atenção:</b> Dados insuficientes para '{produto_ia}' ({marca_ia}). Necessário mínimo de 10 dias de histórico para garantir precisão estatística.
            </div><br>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color: #1A1A1A; padding: 15px; border-radius: 8px; border-left: 5px solid #FF4B4B; color: #FFF;">
                 <b>Base de conhecimento pronta:</b> {len(df_alvo)} registros encontrados para este produto.
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
            
            tab_simulacao, tab_tecnica = st.tabs([" Painel de Simulação", " Painel estatístico"])
            
            with tab_simulacao:
                st.markdown("### 2. Configurar Cenário Futuro")
                st.write("Ajuste as variáveis abaixo para simular o comportamento do mercado.")
                
                with st.container():
                    col_in0, col_in1, col_in2, col_in3, col_in4 = st.columns(5)
                    
                    import datetime
                    hoje = datetime.datetime.now()
                    ano_atual = hoje.year
                    mes_atual_idx = hoje.month - 1
                    
                    with col_in0:
                        ano_selecionado = st.selectbox("Ano da Projeção:", [ano_atual, ano_atual + 1, ano_atual + 2])
                    
                    meses_nomes_lista = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
                    
                    if ano_selecionado == ano_atual:
                        meses_opcoes = meses_nomes_lista[mes_atual_idx:]
                    else:
                        meses_opcoes = meses_nomes_lista
                    
                    with col_in1:
                        mes_selecionado_nome = st.selectbox("Mês da Projeção:", meses_opcoes)
                        mes_alvo_num = meses_nomes_lista.index(mes_selecionado_nome) + 1
                    
                    if 'Dolar' in df_alvo.columns and not df_alvo['Dolar'].isna().all():
                        dolar_recente = df_alvo.sort_values('DataCaptura', ascending=False)['Dolar'].iloc[0]
                    else:
                        dolar_recente = 5.00
                        
                    try:
                        df_nosso_recente = df_interno[(df_interno['Produto'].str.contains(produto_ia, case=False)) & (df_interno['Marca'] == marca_ia)]
                        if not df_nosso_recente.empty:
                            preco_recente_nosso = df_nosso_recente.sort_values('DataCaptura', ascending=False)['Preco'].iloc[0]
                        else:
                            preco_recente_nosso = df_alvo.sort_values('DataCaptura', ascending=False)['Preco'].iloc[0]
                    except:
                        preco_recente_nosso = 0.0

                    try:
                        df_conc_recente = df_aws[(df_aws['Produto'].str.contains(produto_ia, case=False)) & (df_aws['Marca'] == marca_ia)]
                        if not df_conc_recente.empty:
                            preco_recente_conc = df_conc_recente.sort_values('DataCaptura', ascending=False)['Preco'].iloc[0]
                        else:
                            preco_recente_conc = df_alvo.sort_values('DataCaptura', ascending=False)['Preco_Concorrencia'].iloc[0]
                    except:
                        preco_recente_conc = 0.0
                    
                    with col_in2:
                        preco_simulado = st.number_input("Seu Preço (R$):", value=float(preco_recente_nosso), step=50.0)
                    with col_in3:
                        preco_conc_simulado = st.number_input("Preço Concorrência (R$):", value=float(preco_recente_conc), step=50.0)
                    with col_in4:
                        dolar_simulado = st.number_input("Cotação do Dólar (R$):", value=float(dolar_recente), step=0.10)

                st.markdown("<br>", unsafe_allow_html=True)

                if st.button("INICIAR PROCESSAMENTO DA INTELIGÊNCIA ARTIFICIAL", use_container_width=True, type="primary"):
                    with st.spinner(f"O Algoritmo está processando o cenário para {mes_selecionado_nome}/{ano_selecionado}..."):
                        time.sleep(1)
                        from sklearn.ensemble import RandomForestRegressor
                        from sklearn.model_selection import train_test_split
                        from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
                        
                        X = df_alvo[['Ano', 'Mes', 'DiaDaSemana', 'Preco', 'Preco_Concorrencia', 'Dolar']]
                        y = df_alvo['Quantidade']
                        
                        X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2, random_state=42)
                        
                        modelo_ia = RandomForestRegressor(n_estimators=100, random_state=42)
                        modelo_ia.fit(X_treino, y_treino)
                        
                        previsoes_teste = modelo_ia.predict(X_teste)
                        acuracia_r2 = r2_score(y_teste, previsoes_teste)
                        erro_mae = mean_absolute_error(y_teste, previsoes_teste)
                        erro_rmse = np.sqrt(mean_squared_error(y_teste, previsoes_teste))
                        
                        st.session_state['ultima_acuracia'] = acuracia_r2
                        st.session_state['ultima_mae'] = erro_mae
                        st.session_state['ultima_rmse'] = erro_rmse
                        st.session_state['ultima_importancia'] = modelo_ia.feature_importances_
                        
                        X_futuro = pd.DataFrame({
                            'Ano': [ano_selecionado],
                            'Mes': [mes_alvo_num],
                            'DiaDaSemana': [4],
                            'Preco': [preco_simulado],
                            'Preco_Concorrencia': [preco_conc_simulado],
                            'Dolar': [dolar_simulado]
                        })
                        
                        previsao_ia = modelo_ia.predict(X_futuro)[0]
                        previsao_arredondada = max(1, int(previsao_ia))
                        
                        faturamento_estimado = previsao_arredondada * preco_simulado
                        
                        df_historico_mes = df_alvo[df_alvo['Mes'] == mes_alvo_num]
                        if not df_historico_mes.empty:
                            media_historica_mes = int(df_historico_mes['Quantidade'].mean())
                        else:
                            media_historica_mes = "N/A (Sem dados)"

                        st.session_state['resultado_simulacao'] = {
                            'produto_alvo': produto_ia,
                            'previsao': previsao_arredondada,
                            'faturamento': faturamento_estimado,
                            'media_historica': media_historica_mes,
                            'mes_nome': mes_selecionado_nome
                        }

                if 'resultado_simulacao' in st.session_state and st.session_state['resultado_simulacao']['produto_alvo'] == produto_ia:
                    res = st.session_state['resultado_simulacao']
                    
                    def formatar_br(valor):
                        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                    st.markdown("###  Resultado da Projeção de Demanda")
                    
                    colA, colB, colC = st.columns(3)
                    with colB:
                        st.metric(" Previsão Principal", f"{res['previsao']} unid.", delta="Volume Esperado", delta_color="off")
                    with colA:
                        st.metric(" Cenário Pessimista", f"{int(res['previsao'] * 0.85)} unid.", delta="-15% Risco", delta_color="inverse")
                    with colC:
                        st.metric(" Cenário Otimista", f"{int(res['previsao'] * 1.15)} unid.", delta="+15% Conversão", delta_color="normal")
                    
                    st.markdown(f"""
                    <div style="background-color: #0D2137; padding: 20px; border-radius: 10px; margin-top: 15px; border-left: 5px solid #0066CC; color: #FFFFFF;">
                        <h4 style="margin-top: 0px; color: #94B3FD;"> Projeção Financeira</h4>
                        <p style="margin-bottom: 5px; font-size: 16px;"><b>Faturamento Bruto Esperado:</b> R$ {formatar_br(res['faturamento'])} <i>(Baseado no preço sugerido)</i></p>
                        <p style="margin-bottom: 0px; font-size: 16px;"><b>Média de Vendas Histórica ({res['mes_nome']}):</b> {res['media_historica']} unid. <i>(O que costumava vender nesta época)</i></p>
                    </div>
                    """, unsafe_allow_html=True)
                        
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("""
                    <div style="background-color: #1A1A1A; padding: 10px; border-radius: 5px; border-left: 5px solid #FF4B4B; color: #FFF;">
                         <b>Análise Concluída:</b>.
                    </div>
                    """, unsafe_allow_html=True)

            with tab_tecnica:
                st.markdown("### Métricas de Validação Científica")
                if 'ultima_acuracia' in st.session_state:
                    acuracia = st.session_state['ultima_acuracia']
                    mae = st.session_state['ultima_mae']
                    rmse = st.session_state['ultima_rmse']
                    importancias = st.session_state['ultima_importancia']
                    
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric("Score de Tendência (R²)", f"{acuracia * 100:.1f}%")
                    with col_m2:
                        st.metric("Erro Médio Absoluto (MAE)", f"{mae:.1f} unid.")
                    with col_m3:
                        st.metric("Erro Quadrático (RMSE)", f"{rmse:.1f} unid.")
                    
                    if acuracia > 0.80:
                        st.markdown("<div style='background-color: #1A1A1A; padding: 10px; border-left: 5px solid #FF4B4B; border-radius: 5px; margin-bottom: 15px; color: #FFF;'> Grau de confiança <b>Excepcional</b>. O modelo prevê a tendência com alta precisão.</div>", unsafe_allow_html=True)
                    elif acuracia > 0.60:
                        st.markdown("<div style='background-color: #0D2137; padding: 10px; border-left: 5px solid #0066CC; border-radius: 5px; margin-bottom: 15px; color: #FFF;'> Grau de confiança <b>Bom</b>. O modelo compreende a dinâmica do mercado.</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='background-color: #330000; padding: 10px; border-left: 5px solid #FF0000; border-radius: 5px; margin-bottom: 15px; color: #FFF;'> Grau de confiança <b>Baixo</b>. O mercado atual está muito instável ou faltam dados.</div>", unsafe_allow_html=True)
                        
                    st.markdown("---")
                    st.markdown("### Importância das Variáveis (O que a IA aprendeu?)")
                    
                    st.markdown("""
                    <div style="background-color: #0D2137; padding: 15px; border-radius: 8px; border-left: 5px solid #0066CC; color: #94B3FD; margin-bottom: 20px;">
                         <b>Como interpretar esta Matriz de Decisão?</b><br>
                        Este gráfico mostra quais os fatores que mais influenciam a venda deste hardware:<br>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    import plotly.express as px
                    df_importancia = pd.DataFrame({
                        "Variável Analisada": ['Ano', 'Mês (Sazonalidade)', 'Dia da Semana', 'Nosso Preço', 'Preço Concorrência', 'Cotação do Dólar'],
                        "Peso na Decisão (%)": importancias * 100
                    }).sort_values('Peso na Decisão (%)', ascending=True)
                    
                    fig_imp = px.bar(
                        df_importancia, 
                        x="Peso na Decisão (%)", 
                        y="Variável Analisada", 
                        orientation='h',
                        title=f"Matriz de Decisão da IA para: {marca_ia} {produto_ia}"
                    )
                    
                    #  Gráfico em Azul Tecnológico
                    fig_imp.update_traces(
                        marker_color='#0066CC',  
                        hovertemplate="<b>%{y}</b><br>Peso: %{x:.1f}%<extra></extra>"
                    )
                    
                    fig_imp.update_layout(
                        showlegend=False,
                        bargap=0.4,       
                        height=400,       
                        xaxis_title="Peso (%) na Decisão de Compra",
                        yaxis_title=None,
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#FFFFFF'),
                        xaxis=dict(showgrid=True, gridcolor='#333333')
                    )
                    
                    st.plotly_chart(fig_imp, use_container_width=True)
                else:
                    st.markdown("""
                    <div style="background-color: #1A1A1A; padding: 10px; border-radius: 5px; border-left: 5px solid #FF4B4B; color: #FFF;">
                         Execute uma simulação para gerar os dados técnicos.
                    </div>
                    """, unsafe_allow_html=True)

# ================= GESTÃO DE DADOS =================
elif menu == "Gestão de Dados":
    st.title("Ingestão, Limpeza e Tratamento")
    st.write("Carregamento e padronização do histórico de vendas.")
    
    if 'dados_brutos' not in st.session_state:
        st.session_state['dados_brutos'] = None
    if 'dados_tratados' not in st.session_state:
        st.session_state['dados_tratados'] = None
    if 'linhas_removidas' not in st.session_state:
        st.session_state['linhas_removidas'] = 0

    st.markdown("---")
    st.write("Padrão Exigido para o CSV")
    st.markdown("""
    <div style="background-color: #0D2137; padding: 15px; border-radius: 8px; border-left: 5px solid #0066CC; color: #94B3FD; margin-bottom: 20px;">
        Para o modelo de Inteligência Artificial cruzar o seu histórico de vendas com os preços da concorrência, o seu ficheiro CSV deve ter <b>exatamente</b> estas colunas (a ordem não importa, mas os nomes devem ser estes, sem acentos):<br>
        * <b>DataCaptura</b> (Data da venda)<br>
        * <b>Marca</b> (Marca da peça, ex: Asus, Gigabyte)<br>
        * <b>Produto</b> (O nome curto limpo, ex: RTX 4060)<br>
        * <b>Descricao</b> (As características extras da peça)<br>
        * <b>Preco</b> (O valor unitário de venda)<br>
        * <b>Quantidade</b> (Quantas unidades foram vendidas neste dia)
    </div>
    """, unsafe_allow_html=True)
    
    arquivo_upload = st.file_uploader("Suba o arquivo CSV de vendas internas:", type=["csv"])
    
    if arquivo_upload is not None:
        try:
            df_teste = pd.read_csv(arquivo_upload)
            
            colunas_obrigatorias = ['DataCaptura', 'Marca', 'Produto', 'Descricao', 'Preco', 'Quantidade']
            colunas_ausentes = [col for col in colunas_obrigatorias if col not in df_teste.columns]
            
            if len(colunas_ausentes) > 0:
                st.markdown(f"""
                <div style="background-color: #330000; padding: 15px; border-radius: 8px; border-left: 5px solid #FF0000; color: #FFF; margin-bottom: 10px;">
                     <b>Erro de Formatação:</b> Faltam as seguintes colunas no seu CSV: {', '.join(colunas_ausentes)}
                </div>
                <div style="background-color: #330000; padding: 15px; border-radius: 8px; border-left: 5px solid #FF0000; color: #FFF;">
                     Ajuste o cabeçalho do seu ficheiro Excel/CSV para coincidir exatamente com as colunas exigidas acima e tente de novo.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.session_state['dados_brutos'] = df_teste
                st.session_state['dados_tratados'] = None
                
        except Exception as e:
            st.markdown(f"""
            <div style="background-color: #330000; padding: 15px; border-radius: 8px; border-left: 5px solid #FF0000; color: #FFF;">
                 <b>Erro ao ler o ficheiro:</b> {e}
            </div>
            """, unsafe_allow_html=True)
    
    if st.session_state['dados_brutos'] is not None:
        st.markdown(f"""
        <div style="background-color: #1A1A1A; padding: 15px; border-radius: 8px; border-left: 5px solid #FF4B4B; color: #FFF; margin-bottom: 15px;">
             <b>Ficheiro validado e carregado com sucesso</b>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(st.session_state['dados_brutos'], use_container_width=True)    
        
        st.markdown("---")
        st.write("Limpeza e Padronização de Dados")
        st.write("Clique abaixo para padronizar os dados internos com a base de dados da Nuvem AWS.")
        
        if st.button("Executar Tratamento de Dados"):
            with st.spinner("A aplicar algoritmos de normalização..."):
                time.sleep(1) 
                
                df_tratado = st.session_state['dados_brutos'].copy()
                tamanho_original = len(df_tratado)
                
                df_tratado.columns = df_tratado.columns.str.strip()
                df_tratado = df_tratado.dropna(how='all')
                df_tratado = df_tratado.loc[:, ~df_tratado.columns.str.contains('^Unnamed')]
                
                colunas_texto = ['Marca', 'Produto', 'Descricao']
                for col in colunas_texto:
                    if col in df_tratado.columns:
                        df_tratado[col] = df_tratado[col].astype(str).str.upper().str.strip()
                        
                        if col == 'Produto':
                            df_tratado['Produto'] = df_tratado['Produto'].apply(lambda x: re.sub(r'^[\d\s-]+\s*', '', str(x)))
                            df_tratado['Produto'] = df_tratado['Produto'].str.strip() 
                
                if 'Preco' in df_tratado.columns:
                    def limpar_moeda_inteligente(valor):
                        if pd.isna(valor): return valor
                        v = str(valor).replace('R$', '').replace(' ', '').strip()
                        
                        if ',' in v:
                            v = v.replace('.', '').replace(',', '.')
                        else:
                            pass 
                            
                        return v

                    df_tratado['Preco'] = df_tratado['Preco'].apply(limpar_moeda_inteligente)
                    df_tratado['Preco'] = pd.to_numeric(df_tratado['Preco'], errors='coerce')
                    df_tratado = df_tratado.dropna(subset=['Preco']) 
                
                if 'Quantidade' in df_tratado.columns:
                    df_tratado['Quantidade'] = pd.to_numeric(df_tratado['Quantidade'], errors='coerce').fillna(0).astype(int)
                    df_tratado = df_tratado[df_tratado['Quantidade'] > 0]
                
                if 'DataCaptura' in df_tratado.columns:
                    df_tratado['DataCaptura'] = pd.to_datetime(df_tratado['DataCaptura'], errors='coerce', dayfirst=True)
                    df_tratado = df_tratado.dropna(subset=['DataCaptura']) 
                    df_tratado['DataCaptura'] = df_tratado['DataCaptura'].dt.strftime('%Y-%m-%d')
                
                st.session_state['dados_tratados'] = df_tratado
                st.session_state['linhas_removidas'] = tamanho_original - len(df_tratado)
                
    if st.session_state['dados_tratados'] is not None:
        st.write("Dados Normalizados e Prontos")
        st.dataframe(st.session_state['dados_tratados'], width='stretch')
        
        st.markdown(f"""
        <div style="background-color: #1A1A1A; padding: 15px; border-radius: 8px; border-left: 5px solid #FF4B4B; color: #FFF; margin-bottom: 15px;">
             <b>Operação concluída!</b> {st.session_state['linhas_removidas']} linhas de "lixo" (ou nulas) removidas. Valores formatados para a IA e datas alinhadas com o banco AWS.
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Limpar Memória e Subir Novo Arquivo"):
            st.session_state['dados_brutos'] = None
            st.session_state['dados_tratados'] = None
            st.session_state['linhas_removidas'] = 0
            st.rerun()