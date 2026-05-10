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

# FUNÇÕES DE DADOS 
@st.cache_data(ttl=600) 
def carregar_dados_aws():
    endpoint_aws = "hardwares-tcc.cveowcsuansb.sa-east-1.rds.amazonaws.com"
    senha_aws = urllib.parse.quote_plus("milanhaverso2")
    usuario_aws = "lcpctcc"
    url_conexao = f"mssql+pyodbc://{usuario_aws}:{senha_aws}@{endpoint_aws}/tcc_hardware?driver=ODBC+Driver+17+for+SQL+Server"
    
    try:
        engine = create_engine(url_conexao)
        df = pd.read_sql("SELECT DataCaptura, Loja, Marca, Produto, Preco FROM HistoricoPrecos", engine) 
        
        # Limpeza: Remove números e hífens isolados no início do nome
        df['Produto'] = df['Produto'].apply(lambda x: re.sub(r'^[\d\s-]+\s*', '', str(x)))
        
        df['DataCaptura'] = pd.to_datetime(df['DataCaptura']) 
        df = df.sort_values('DataCaptura')
        return df
    except Exception as e:
        st.error(f"Erro ao conectar na AWS: {e}")
        return pd.DataFrame()

# MENU LATERAL 
st.sidebar.title("Menu")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegação do Sistema:",
    ["Pesquisa de Mercado", 
     "Sistema de predição", 
     "Gestão de Dados"]
)

# DASHBOARD 
if menu == "Pesquisa de Mercado":
    st.title("Scanner / Dashbords do mercado")
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
            st.info("Digite a família da peça (Ex: RTX 5070, B650, RX 7600) e o devolvera a média de preços de todos os modelos daquela linha no dia.")
            
            # SOLUÇÃO DO RESET: Usa a memória do Streamlit
            if 'ultima_busca' not in st.session_state:
                st.session_state['ultima_busca'] = "rtx 5070" 
                
            familia_input = st.text_input("Digite a Família do Hardware:", value=st.session_state['ultima_busca'])
            
            # Atualiza a memória com o que o usuário acabou de digitar
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
                palavras_busca = command = busca_limpa.split()
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
                    fig.update_traces(textposition="top center")
                    fig.update_layout(yaxis=dict(range=[df_agrupado['Preco'].min() * 0.9, df_agrupado['Preco'].max() * 1.1])) 
                    fig.update_xaxes(tickformat="%d/%m/%Y")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"Sem dados históricos para a família '{familia_input}'.")
                    
        # CORREÇÃO AQUI: "Visão Específica" em vez de "Específica"
        elif modo_visao == "Visão Específica":
            #VISÃO ESPECÍFICA 
            st.info("Selecione o modelo exato para analisar o preço dele.")
            
            # FILTRO ESTRITO DE PRODUTO ESPECÍFICO
            pesquisa_produto = st.text_input("Filtre pela família/marca do produto:")
            
            if pesquisa_produto:
                # Puxa só os produtos que realmente CONTÊM a palavra junta (case-insensitive)
                lista_filtrada = df_historico[df_historico['Produto'].str.contains(pesquisa_produto, case=False, na=False)]['Produto'].dropna().unique()
                lista_filtrada = sorted(lista_filtrada)
            else:
                # Se não digitou nada, mostra a mensagem e deixa a lista "vazia"
                lista_filtrada = ["Digite algo na pesquisa acima para encontrar o produto"]
                
            # Descobre se a caixinha deve ficar bloqueada ou não
            esta_bloqueado = len(lista_filtrada) == 1 and lista_filtrada[0].startswith("Digite algo")
            
            produto_escolhido = st.selectbox(
                "Escolha o Hardware específico:", 
                lista_filtrada,
                disabled=esta_bloqueado
            )
            
            # Trava de segurança: Só prossegue se houver realmente um produto escolhido válido
            if produto_escolhido and not esta_bloqueado:
                df_filtrado = df_historico[df_historico['Produto'] == produto_escolhido].copy()
                
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
                    
                    fig.update_traces(textposition="top center")
                    fig.update_layout(yaxis=dict(range=[df_filtrado['Preco'].min() * 0.9, df_filtrado['Preco'].max() * 1.1]))
                    fig.update_xaxes(tickformat="%d/%m/%Y")
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Sem dados suficientes para gerar o gráfico deste produto específico.")
            else:
                 st.info("Por favor, pesquise e selecione um produto na lista acima.")
        
        # NOVO MÓDULO: ANÁLISE DRILL-DOWN (CASCATA INTELIGENTE)

        st.markdown("---")
        st.write("Análise De Filtros Avançados")
        st.write("Filtre o mercado através de categorias, modelos, marcas e especificações para encontrar nichos exatos.")
        
        # Categorias principais
        categorias_base = [
            "Placa de Vídeo", "Processador", "Placa Mãe", "Memória RAM", "SSD", "HD", 
            "Monitor", "Fonte", "Gabinete", "Water Cooler", "Air Cooler", "Fan",
            "Mouse Gamer", "Mouse", "Teclado Mecânico", "Teclado Magnético", "Headset Gamer",
            "Mousepad Gamer", "Webcam", "Soundbar", "Microfone"
        ]

        # DICIONÁRIO DE MODELOS MAPEADO 100%
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
            "Memória RAM": ["8GB", "16GB", "32GB", "64GB", "DDR4", "DDR5"],
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

        todos_os_modelos = sorted(list(set(sum(mapa_subcategorias.values(), []))))
        
        col1, col2, col3, col4 = st.columns(4)
        
        # 1. CATEGORIA -
        with col1:
            cat_escolhida = st.selectbox("1. Categoria (Opcional):", [""] + sorted(categorias_base))
            
        # 2. MODELO (Filtra baseado na Categoria) 
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
            subcat_escolhida = st.selectbox("2. Modelo (Opcional):", opcoes_modelo, disabled=disabled_mod)

        # APLICANDO OS PRIMEIROS FILTROS NA MEMÓRIA PARA DESCOBRIR AS MARCAS
        df_drill = df_historico.copy()
        
        if cat_escolhida:
            termo_cat_limpo = ''.join(c for c in unicodedata.normalize('NFD', cat_escolhida) if unicodedata.category(c) != 'Mn').lower()
            if termo_cat_limpo == "placa de video":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('video|vídeo|vga|geforce|radeon|rtx|gtx|rx|arc', na=False)]
            elif termo_cat_limpo == "placa mae":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('placa|motherboard|mainboard', na=False)]
            elif termo_cat_limpo == "memoria ram":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('memoria|ram|ddr', na=False)]
            elif "fonte" in termo_cat_limpo:
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('fonte|atx|power', na=False)]
            elif termo_cat_limpo == "mouse":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('mouse', na=False) & ~df_drill['Produto'].str.lower().str.contains('gamer', na=False)]
            elif termo_cat_limpo == "mouse gamer":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('mouse', na=False) & df_drill['Produto'].str.lower().str.contains('gamer', na=False)]
            elif termo_cat_limpo == "teclado mecanico":
                 df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('teclado', na=False) & df_drill['Produto'].str.lower().str.contains('mecanico|mecânico', na=False)]
            elif termo_cat_limpo == "teclado magnetico":
                 df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('teclado', na=False) & df_drill['Produto'].str.lower().str.contains('magnetico|magnético', na=False)]
            else:
                 for palavra in termo_cat_limpo.split():
                     df_drill = df_drill[df_drill['Produto'].str.lower().str.contains(palavra, na=False)]
                     
        if subcat_escolhida and subcat_escolhida != "N/A":
            termo_sub_sem_espaco = subcat_escolhida.lower().replace(" ", "")
            mask = df_drill['Produto'].str.lower().str.replace(" ", "").str.contains(termo_sub_sem_espaco, na=False)
            
            if not any(sufixo in termo_sub_sem_espaco for sufixo in ['ti', 'super', 'xt']):
                mask = mask & ~df_drill['Produto'].str.lower().str.replace(" ", "").str.contains(f"{termo_sub_sem_espaco}ti", na=False)
                mask = mask & ~df_drill['Produto'].str.lower().str.replace(" ", "").str.contains(f"{termo_sub_sem_espaco}super", na=False)
                mask = mask & ~df_drill['Produto'].str.lower().str.replace(" ", "").str.contains(f"{termo_sub_sem_espaco}xt", na=False)
            
            df_drill = df_drill[mask]

        # 3. MARCAS
        marcas_validas = sorted([m for m in df_drill['Marca'].dropna().unique()])
        
        with col3:
            marcas_escolhidas = st.multiselect("3. Marcas (Opcional):", marcas_validas)
            
        if len(marcas_escolhidas) > 0:
            df_drill = df_drill[df_drill['Marca'].isin(marcas_escolhidas)]

        # 4. ESPECIFICAÇÃO
        with col4:
            especificacao_extra = st.text_input("4. Especificação (Ex: Branco, OC):")
            
        if especificacao_extra:
            espec_limpa = ''.join(c for c in unicodedata.normalize('NFD', especificacao_extra) if unicodedata.category(c) != 'Mn').lower()
            df_drill = df_drill[df_drill['Produto'].str.lower().str.contains(espec_limpa, na=False)]

       
        # REGRA DAS 2 OPÇÕES E GERAÇÃO DO GRÁFICO
   
        filtros_ativos = 0
        if cat_escolhida: filtros_ativos += 1
        if subcat_escolhida and subcat_escolhida != "N/A": filtros_ativos += 1
        if len(marcas_escolhidas) > 0: filtros_ativos += 1
        if especificacao_extra: filtros_ativos += 1

        if filtros_ativos < 2:
            st.info(" Preencha pelo menos **DUAS opções** (Ex: Categoria + Marca, ou Modelo + Marca) para visualizar o histórico de preços.")
        else:
            if not df_drill.empty:
                
                #NOVO: FILTRO DE PREÇO NO CANTO SUPERIOR DIREITO (ATUALIZADO)
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
                
                # Aplica o filtro de preço
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
                    # Agrupamento para o Gráfico
                    if subcat_escolhida != "" and subcat_escolhida != "N/A":
                        df_agrupado_drill = df_drill.groupby(['DataCaptura', 'Loja', 'Marca'])['Preco'].mean().reset_index()
                        df_agrupado_drill['Legenda'] = df_agrupado_drill['Loja'] + " - " + df_agrupado_drill['Marca']
                    else:
                        df_agrupado_drill = df_drill.groupby(['DataCaptura', 'Loja', 'Produto'])['Preco'].mean().reset_index()
                        df_agrupado_drill['Produto_Curto'] = df_agrupado_drill['Produto'].apply(lambda x: x[:40] + "..." if len(x) > 40 else x)
                        df_agrupado_drill['Legenda'] = df_agrupado_drill['Loja'] + " - " + df_agrupado_drill['Produto_Curto']
                    
                    df_agrupado_drill['Preco_Label'] = df_agrupado_drill['Preco'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    
                    partes_titulo = []
                    if cat_escolhida: partes_titulo.append(cat_escolhida)
                    if subcat_escolhida and subcat_escolhida != "N/A": partes_titulo.append(subcat_escolhida)
                    if marcas_escolhidas: partes_titulo.append(" | ".join(marcas_escolhidas))
                    
                    titulo_graf = " + ".join(partes_titulo)
                    subtitulo = f"Especificação: {especificacao_extra}" if especificacao_extra else ""
                    
                    fig_drill = px.line(
                        df_agrupado_drill, 
                        x="DataCaptura", 
                        y="Preco", 
                        color="Legenda", 
                        markers=True, 
                        text="Preco_Label", 
                        title=f"Drill-Down: {titulo_graf} {subtitulo}", 
                        labels={"DataCaptura": "Data da Extração", "Preco": "Preço Médio (R$)", "Legenda": "Item"}
                    )
                    
                    fig_drill.update_traces(textposition="top center")
                    fig_drill.update_layout(yaxis=dict(range=[df_agrupado_drill['Preco'].min() * 0.9, df_agrupado_drill['Preco'].max() * 1.1]))
                    fig_drill.update_xaxes(tickformat="%d/%m/%Y")
                    
                    st.plotly_chart(fig_drill, use_container_width=True)
                    
                    # NOVO: TABELA DE EXTRATO DOS ÚLTIMOS 7 DIAS COM VALORES REAIS
                    with st.expander("Ver histórico detalhado de preços (Últimos 7 dias)"):
                        df_tabela = df_drill.copy()
                        df_tabela['DataCaptura'] = pd.to_datetime(df_tabela['DataCaptura'])
                        
                        # Filtra pegando a data mais recente no dataframe e voltando 7 dias
                        data_maxima = df_tabela['DataCaptura'].max()
                        data_limite = data_maxima - pd.Timedelta(days=7)
                        df_7_dias = df_tabela[df_tabela['DataCaptura'] >= data_limite].copy()
                        
                        # Formatação visual
                        df_7_dias['Data'] = df_7_dias['DataCaptura'].dt.strftime('%d/%m/%Y')
                        df_7_dias['Preço Real'] = df_7_dias['Preco'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                        
                        st.dataframe(
                            df_7_dias.sort_values(['Produto', 'DataCaptura'], ascending=[True, False])[['Data', 'Loja', 'Marca', 'Produto', 'Preço Real']],
                            width='stretch',
                            hide_index=True
                        )
                else:
                    st.warning(f"Nenhum produto encontrado na faixa '{filtro_preco}'.")
            else:
                st.warning("Nenhum hardware encontrado no banco de dados com essa combinação exata de filtros.")
# ================= PÁGINA 2: PREVISÃO DE IA =================
elif menu == "Sistema de predição":
    st.title("🔮 Motor de Previsão de Vendas (Machine Learning)")
    st.write("Treinando o algoritmo Random Forest com dados históricos e do mercado para prever a demanda futura.")

    # 1. TRAVA DE SEGURANÇA: Exige os dados da aba "Gestão de Dados"
    if st.session_state.get('dados_tratados') is None:
        st.warning("⚠️ Atenção: A Inteligência Artificial precisa dos seus dados internos para aprender!")
        st.info("Vá até a aba **'Gestão de Dados'**, faça o upload do seu ficheiro CSV de vendas e clique em 'Executar Tratamento de Dados' primeiro.")
    else:
        # Carregando os dois mundos
        df_interno = st.session_state['dados_tratados'].copy()
        df_aws = carregar_dados_aws()

        with st.spinner("Cruzando dados internos com a nuvem AWS e preparando variáveis..."):
            # Garantindo tipos de dados corretos no CSV interno
            df_interno['DataCaptura'] = pd.to_datetime(df_interno['DataCaptura'])
            df_interno['Preco'] = pd.to_numeric(df_interno['Preco'], errors='coerce')
            df_interno['Quantidade'] = pd.to_numeric(df_interno['Quantidade'], errors='coerce')
            df_interno = df_interno.dropna(subset=['Preco', 'Quantidade'])

            # Preparando dados da AWS (Concorrência)
            if not df_aws.empty:
                df_aws['DataCaptura'] = pd.to_datetime(df_aws['DataCaptura']).dt.normalize() # Tira as horas
                df_aws['Produto'] = df_aws['Produto'].str.upper().str.strip() # Padroniza maiúsculo igual o CSV
                
                # Agrupa os preços da concorrência por dia e produto (Tira a média se Kabum e Tera tiverem o mesmo)
                df_concorrencia = df_aws.groupby(['DataCaptura', 'Produto'])['Preco'].mean().reset_index()
                df_concorrencia = df_concorrencia.rename(columns={'Preco': 'Preco_Concorrencia'})
                
                # 🚀 O GRANDE MERGE: Junta CSV Interno + Concorrência AWS
                df_ml = pd.merge(df_interno, df_concorrencia, on=['DataCaptura', 'Produto'], how='left')
                
                # Se a concorrência não vendeu aquele produto naquele dia, a IA assume o nosso próprio preço como base do mercado
                df_ml['Preco_Concorrencia'] = df_ml['Preco_Concorrencia'].fillna(df_ml['Preco'])
            else:
                # Fallback caso a AWS falhe
                df_ml = df_interno.copy()
                df_ml['Preco_Concorrencia'] = df_ml['Preco']

            # 🚀 FEATURE ENGINEERING (Criando variáveis exógenas)
            df_ml['Mes'] = df_ml['DataCaptura'].dt.month
            df_ml['DiaDaSemana'] = df_ml['DataCaptura'].dt.dayofweek

        # Lista de produtos disponíveis no CSV da empresa
        produtos_disponiveis = sorted(df_ml['Produto'].unique())
        
        col1, col2 = st.columns(2)
        with col1:
            produto_ia = st.selectbox("Selecione o Hardware para Análise Preditiva:", produtos_disponiveis)
        
        # Filtra o dataframe apenas para o produto escolhido
        df_alvo = df_ml[df_ml['Produto'] == produto_ia].copy()
        
        # Só treina se tiver histórico suficiente (ex: mais de 10 dias de venda)
        if len(df_alvo) < 10:
            st.error(f"🚨 Histórico insuficiente para o produto '{produto_ia}'. O algoritmo precisa de mais de 10 registros de venda para aprender padrões.")
        else:
            with col2:
                st.info(f"Registros de vendas encontrados para treinamento: **{len(df_alvo)} dias**")
                
            st.markdown("---")
            st.write("### ⚙️ Simulação de Cenário Futuro")
            
            # Inputs do usuário para a predição futura
            col_in1, col_in2, col_in3 = st.columns(3)
            with col_in1:
                mes_alvo = st.slider("Mês Futuro (1=Jan a 12=Dez):", 1, 12, 6)
            with col_in2:
                preco_simulado = st.number_input("Seu Preço Simulado (R$):", value=float(df_alvo['Preco'].mean()))
            with col_in3:
                preco_conc_simulado = st.number_input("Preço Simulado Concorrência (R$):", value=float(df_alvo['Preco_Concorrencia'].mean()))

            if st.button("🚀 Treinar IA e Gerar Previsão"):
                with st.spinner(f"Treinando o modelo Random Forest para {produto_ia}..."):
                    from sklearn.ensemble import RandomForestRegressor
                    from sklearn.model_selection import train_test_split
                    from sklearn.metrics import r2_score
                    
                    # 1. Definindo X (Exógenas/Features) e Y (Endógena/Target)
                    X = df_alvo[['Mes', 'DiaDaSemana', 'Preco', 'Preco_Concorrencia']]
                    y = df_alvo['Quantidade']
                    
                    # 2. Divisão de Treino (80%) e Teste (20%)
                    X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2, random_state=42)
                    
                    # 3. Treinamento
                    modelo_ia = RandomForestRegressor(n_estimators=100, random_state=42)
                    modelo_ia.fit(X_treino, y_treino)
                    
                    # 4. Avaliação (Acurácia)
                    previsoes_teste = modelo_ia.predict(X_teste)
                    acuracia_r2 = r2_score(y_teste, previsoes_teste)
                    
                    # 5. Predição do cenário simulado (Assumindo que seja uma sexta-feira = 4)
                    X_futuro = pd.DataFrame({
                        'Mes': [mes_alvo],
                        'DiaDaSemana': [4], # Sexta-feira
                        'Preco': [preco_simulado],
                        'Preco_Concorrencia': [preco_conc_simulado]
                    })
                    
                    previsao_ia = modelo_ia.predict(X_futuro)[0]
                    previsao_arredondada = max(1, int(previsao_ia)) # Nunca prevê menos que 1
                    
                    st.success(f"✅ Treinamento concluído! A Inteligência Artificial analisou os padrões de '{produto_ia}'.")
                    
                    # Mostra a margem de acerto para a banca ver que é Machine Learning real
                    st.caption(f"🎯 **Acurácia do Modelo (R² Score):** {acuracia_r2:.2f} (O quão bem a IA aprendeu com os testes)")
                    
                    st.markdown("### Cenários Projetados para o Mês Selecionado")
                    colA, colB, colC = st.columns(3)
                    colA.metric("📉 Cenário Pessimista", f"{int(previsao_arredondada * 0.85)} unid.")
                    colB.metric("🎯 Previsão Principal", f"{previsao_arredondada} unid.", "Unidades Estimadas")
                    colC.metric("📈 Cenário Otimista", f"{int(previsao_arredondada * 1.15)} unid.")
                    
                    # Bônus pro TCC: Feature Importance (O que mais afetou a venda?)
                    st.markdown("---")
                    st.markdown("### 🧠 O que a IA descobriu? (Importância das Variáveis)")
                    importancias = modelo_ia.feature_importances_
                    df_importancia = pd.DataFrame({
                        "Variável": ['Mês do Ano', 'Dia da Semana', 'Seu Preço', 'Preço Concorrência'],
                        "Peso (%)": importancias * 100
                    }).sort_values('Peso (%)', ascending=False)
                    
                    fig_imp = px.bar(df_importancia, x="Variável", y="Peso (%)", title="Quais fatores mais influenciaram a venda?", color="Variável")
                    st.plotly_chart(fig_imp, use_container_width=True)
                    
                    st.info("💡 **Dica Técnica para a Monografia:** A IA não apenas prevê o futuro, mas analisa a 'Feature Importance' para nos dizer matematicamente se o consumidor deste produto liga mais para a época do ano (Sazonalidade) ou se é mais sensível à Guerra de Preços (Seu Preço vs Concorrência).")
#PÁGINA 3: GESTÃO DE DADOS 
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
    st.info("""
    Para o modelo de Inteligência Artificial cruzar o seu histórico de vendas com os preços da concorrência, o seu ficheiro CSV deve ter **exatamente** estas colunas (a ordem não importa, mas os nomes devem ser estes, sem acentos):
    * **DataCaptura** (Data da venda)
    * **Marca** (Marca da peça, ex: Asus, Gigabyte)
    * **Produto** (O nome curto limpo, ex: RTX 4060)
    * **Descricao** (As características extras da peça)
    * **Preco** (O valor unitário de venda)
    * **Quantidade** (Quantas unidades foram vendidas neste dia)
    """)
    
    arquivo_upload = st.file_uploader("Suba o arquivo CSV de vendas internas:", type=["csv"])
    
    if arquivo_upload is not None:
        try:
            df_teste = pd.read_csv(arquivo_upload)
            
            colunas_obrigatorias = ['DataCaptura', 'Marca', 'Produto', 'Descricao', 'Preco', 'Quantidade']
            colunas_ausentes = [col for col in colunas_obrigatorias if col not in df_teste.columns]
            
            if len(colunas_ausentes) > 0:
                st.error(f"Erro de Formatação Faltam as seguintes colunas no seu CSV: {', '.join(colunas_ausentes)}")
                st.warning("Ajuste o cabeçalho do seu ficheiro Excel/CSV para coincidir exatamente com as colunas exigidas acima e tente de novo.")
            else:
                st.session_state['dados_brutos'] = df_teste
                st.session_state['dados_tratados'] = None
                
        except Exception as e:
            st.error(f"Erro ao ler o ficheiro: {e}")
    
    if st.session_state['dados_brutos'] is not None:
        st.success("Ficheiro validado e carregado com sucesso")
        st.dataframe(st.session_state['dados_brutos'], width='stretch')
        
        st.markdown("---")
        st.write("Limpeza e Padronização de Dados")
        st.write("Clique abaixo para padronizar os dados internos com a base de dados da Nuvem AWS.")
        
        if st.button("Executar Tratamento de Dados"):
            with st.spinner("A aplicar algoritmos de normalização..."):
                import time
                time.sleep(1) 
                
                df_tratado = st.session_state['dados_brutos'].copy()
                
                # 1. Limpa nomes das colunas e dropa linhas 100% vazias
                df_tratado.columns = df_tratado.columns.str.strip()
                df_tratado = df_tratado.dropna(how='all')
                
                # 2. NOVO: Remove colunas de índice "fantasmas" (ex: Unnamed: 0) que o Excel ou Pandas criam
                df_tratado = df_tratado.loc[:, ~df_tratado.columns.str.contains('^Unnamed')]
                
                # 3. Normalização de Texto (Maiúsculo + Regex)
                colunas_texto = ['Marca', 'Produto', 'Descricao']
                for col in colunas_texto:
                    if col in df_tratado.columns:
                        # Deixa tudo em CAIXA ALTA e remove espaços nas pontas
                        df_tratado[col] = df_tratado[col].astype(str).str.upper().str.strip()
                        
                        # NOVO: Se for a coluna Produto, corta os códigos/hífens do início para bater com a AWS
                        if col == 'Produto':
                            import re
                            df_tratado['Produto'] = df_tratado['Produto'].apply(lambda x: re.sub(r'^[\d\s-]+\s*', '', str(x)))
                            df_tratado['Produto'] = df_tratado['Produto'].str.strip() # Tira o espaço caso sobre depois do corte
                    
                # 4. Formatação de Data
                if 'DataCaptura' in df_tratado.columns:
                     try:
                         df_tratado['DataCaptura'] = pd.to_datetime(df_tratado['DataCaptura']).dt.date
                     except:
                         pass 
                
                st.session_state['dados_tratados'] = df_tratado
                st.session_state['linhas_removidas'] = len(st.session_state['dados_brutos']) - len(df_tratado)
                
    if st.session_state['dados_tratados'] is not None:
        st.write("Dados Normalizados e Prontos")
        st.dataframe(st.session_state['dados_tratados'], width='stretch')
        
        st.success(f"Operação concluída! {st.session_state['linhas_removidas']} linhas inválidas removidas. Nomenclatura em CAIXA ALTA e datas alinhadas com o banco AWS.")
        
        if st.button("Limpar Memória e Subir Novo Arquivo"):
            st.session_state['dados_brutos'] = None
            st.session_state['dados_tratados'] = None
            st.session_state['linhas_removidas'] = 0
            st.rerun()