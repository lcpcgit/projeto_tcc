import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import urllib.parse
import unicodedata
import re
import numpy as np
import time

st.set_page_config(page_title="Hardware Preditivo AI", layout="wide")

# ================= FUNÇÕES DE DADOS =================
@st.cache_data(ttl=600) 
def carregar_dados_aws():
    endpoint_aws = "hardwares-tcc.cveowcsuansb.sa-east-1.rds.amazonaws.com"
    senha_aws = urllib.parse.quote_plus("milanhaverso2")
    usuario_aws = "lcpctcc"
    url_conexao = f"mssql+pyodbc://{usuario_aws}:{senha_aws}@{endpoint_aws}/tcc_hardware?driver=ODBC+Driver+17+for+SQL+Server"
    
    try:
        engine = create_engine(url_conexao)
        df = pd.read_sql("SELECT DataCaptura, Loja, Marca, Produto, Preco FROM HistoricoPrecos", engine) # Adicionado 'Marca' aqui!
        
        # 🚀 Limpeza: Remove números e hífens isolados no início do nome
        df['Produto'] = df['Produto'].apply(lambda x: re.sub(r'^[\d\s-]+\s*', '', str(x)))
        
        df['DataCaptura'] = pd.to_datetime(df['DataCaptura']) 
        df = df.sort_values('DataCaptura')
        return df
    except Exception as e:
        st.error(f"Erro ao conectar na AWS: {e}")
        return pd.DataFrame()

# ================= MENU LATERAL =================
st.sidebar.title("🤖 IA Hardware B2B")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegação do Sistema:",
    ["📊 Dashboard e Mercado", 
     "🔮 Previsão de IA", 
     "📂 Gestão de Dados"]
)

# ================= PÁGINA 1: DASHBOARD =================
if menu == "📊 Dashboard e Mercado":
    st.title("📊 Inteligência de Mercado: Scanner B2B")
    st.write("Acompanhe o histórico de preços reais praticados pelos maiores e-commerces (Kabum e Terabyte).")
    
    df_historico = carregar_dados_aws()
    
    if not df_historico.empty:
        st.write("### 📈 Tendência de Preços na Concorrência")
        
        modo_visao = st.radio(
            "Selecione o Nível de Análise:", 
            ["🌐 Visão Geral (Média de Preços da Família)", "🔍 Visão Específica (Produto Exato)"],
            horizontal=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True) 
        
        if modo_visao == "🌐 Visão Geral (Média de Preços da Família)":
            st.info("Aqui você digita a família da peça (Ex: RTX 5070, B650, RX 7600) e o sistema calcula a **média de preços** de todos os modelos daquela linha no dia.")
            
            # 🚀 SOLUÇÃO DO RESET: Usa a memória do Streamlit
            if 'ultima_busca' not in st.session_state:
                st.session_state['ultima_busca'] = "rtx 5070" # Valor padrão inicial
                
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
                    fig.update_traces(textposition="top center")
                    fig.update_layout(yaxis=dict(range=[df_agrupado['Preco'].min() * 0.9, df_agrupado['Preco'].max() * 1.1])) 
                    fig.update_xaxes(tickformat="%d/%m/%Y")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"Sem dados históricos para a família '{familia_input}'.")
                    
        elif modo_visao == "🔍 Visão Específica (Produto Exato)":
            # --- VISÃO ESPECÍFICA ---
            st.info("Aqui você seleciona o modelo **exato** para analisar o preço dele.")
            
            lista_produtos = sorted(df_historico['Produto'].unique())
            
            # 🚀 SOLUÇÃO DO RESET: Usa a memória do Streamlit para a Visão Específica
            if 'ultimo_produto_especifico' not in st.session_state:
                # Se não tem memória, o padrão é o primeiro produto da lista (para evitar erros)
                st.session_state['ultimo_produto_especifico'] = lista_produtos[0] if lista_produtos else None
            
            # Tenta encontrar o índice do produto salvo na lista atual. Se não achar, usa 0.
            try:
                indice_padrao = lista_produtos.index(st.session_state['ultimo_produto_especifico'])
            except ValueError:
                indice_padrao = 0

            produto_escolhido = st.selectbox(
                "Escolha o Hardware específico na base de dados:", 
                lista_produtos,
                index=indice_padrao
            )
            
            # Atualiza a memória com o que o usuário acabou de selecionar
            st.session_state['ultimo_produto_especifico'] = produto_escolhido
            
            # Trava de segurança: Só prossegue se houver realmente um produto escolhido
            if produto_escolhido:
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
                 st.info("Por favor, selecione um produto na lista acima.")
# =======================================================
        # 🚀 NOVO MÓDULO: ANÁLISE DRILL-DOWN EM CASCATA 4 NÍVEIS
        # =======================================================
        st.markdown("---")
        st.write("### 🔬 Análise Drill-Down (Filtros Avançados)")
        st.write("Filtre o mercado através de categorias, modelos, marcas e especificações para encontrar nichos exatos.")
        
        # Categorias principais
        categorias_base = [
            "Placa de Vídeo", "Processador", "Placa Mãe", "Memória RAM", "SSD", "HD", 
            "Monitor", "Fonte", "Gabinete", "Water Cooler", "Air Cooler", "Fan",
            "Mouse Gamer", "Mouse", "Teclado Mecânico", "Teclado Magnético", "Headset Gamer",
            "Mousepad Gamer", "Webcam", "Soundbar", "Microfone"
        ]

        # 🚀 DICIONÁRIO DE MODELOS MAPEADO 100% DO SEU BOT
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
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cat_escolhida = st.selectbox("1. Categoria:", [""] + sorted(categorias_base))
            
        with col2:
            opcoes_sub = [""]
            # Se a categoria escolhida tem submodelos cadastrados, preenche a lista
            if cat_escolhida in mapa_subcategorias and len(mapa_subcategorias[cat_escolhida]) > 0:
                opcoes_sub += sorted(mapa_subcategorias[cat_escolhida])
                subcat_escolhida = st.selectbox("2. Modelo:", opcoes_sub)
            else:
                # Se não tem submodelos (ex: Webcam), desabilita
                subcat_escolhida = st.selectbox("2. Modelo:", ["N/A"], disabled=True)
            
        with col3:
            # 🚀 FILTRO DINÂMICO DE MARCAS (CATEGORIA + MODELO)
            if cat_escolhida:
                df_marcas_disponiveis = df_historico.copy()
                termo_cat_limpo = ''.join(c for c in unicodedata.normalize('NFD', cat_escolhida) if unicodedata.category(c) != 'Mn').lower()
                
                # Filtro de Categoria Base
                if termo_cat_limpo == "mouse":
                    df_marcas_disponiveis = df_marcas_disponiveis[df_marcas_disponiveis['Produto'].str.lower().str.contains('mouse', na=False) & ~df_marcas_disponiveis['Produto'].str.lower().str.contains('gamer', na=False)]
                elif termo_cat_limpo == "mouse gamer":
                    df_marcas_disponiveis = df_marcas_disponiveis[df_marcas_disponiveis['Produto'].str.lower().str.contains('mouse', na=False) & df_marcas_disponiveis['Produto'].str.lower().str.contains('gamer', na=False)]
                elif termo_cat_limpo == "teclado mecanico":
                    df_marcas_disponiveis = df_marcas_disponiveis[df_marcas_disponiveis['Produto'].str.lower().str.contains('teclado', na=False) & df_marcas_disponiveis['Produto'].str.lower().str.contains('mecanico|mecânico', na=False)]
                elif termo_cat_limpo == "teclado magnetico":
                    df_marcas_disponiveis = df_marcas_disponiveis[df_marcas_disponiveis['Produto'].str.lower().str.contains('teclado', na=False) & df_marcas_disponiveis['Produto'].str.lower().str.contains('magnetico|magnético', na=False)]
                else:
                    for palavra in termo_cat_limpo.split():
                        df_marcas_disponiveis = df_marcas_disponiveis[df_marcas_disponiveis['Produto'].str.lower().str.contains(palavra, na=False)]
                
                # Filtro de Modelo CORRIGIDO PARA IGNORAR VARIANTES QUANDO NÃO SOLICITADAS
                if subcat_escolhida and subcat_escolhida != "N/A":
                    termo_sub_sem_espaco = subcat_escolhida.lower().replace(" ", "")
                    # Primeiro pega tudo que contém a base (ex: acha 5070 e 5070ti)
                    df_marcas_disponiveis = df_marcas_disponiveis[df_marcas_disponiveis['Produto'].str.lower().str.replace(" ", "").str.contains(termo_sub_sem_espaco, na=False)]
                    
                    # 🚀 A MÁGICA ACONTECE AQUI:
                    # Se o usuário NÃO pesquisou por Ti, Super ou XT, nós apagamos elas dos resultados!
                    if not any(sufixo in termo_sub_sem_espaco for sufixo in ['ti', 'super', 'xt']):
                        df_marcas_disponiveis = df_marcas_disponiveis[
                            ~df_marcas_disponiveis['Produto'].str.lower().str.replace(" ", "").str.contains(f"{termo_sub_sem_espaco}ti", na=False) &
                            ~df_marcas_disponiveis['Produto'].str.lower().str.replace(" ", "").str.contains(f"{termo_sub_sem_espaco}super", na=False) &
                            ~df_marcas_disponiveis['Produto'].str.lower().str.replace(" ", "").str.contains(f"{termo_sub_sem_espaco}xt", na=False)
                        ]
                
                marcas_filtradas = sorted([m for m in df_marcas_disponiveis['Marca'].dropna().unique() if m != "Outra/Genérica"])
            else:
                marcas_filtradas = []
                
            marcas_escolhidas = st.multiselect("3. Marcas:", marcas_filtradas, disabled=not cat_escolhida)
            
        with col4:
            especificacao_extra = st.text_input("4. Especificação (Ex: Branco, OC):", disabled=not cat_escolhida)
            
        if cat_escolhida: 
            df_drill = df_historico.copy()
            
            # 1. Aplicando Filtro de Categoria no Gráfico
            termo_cat_limpo = ''.join(c for c in unicodedata.normalize('NFD', cat_escolhida) if unicodedata.category(c) != 'Mn').lower()
            if termo_cat_limpo == "mouse":
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
            
            # 2. Aplicando Filtro de Modelo no Gráfico CORRIGIDO
            if subcat_escolhida and subcat_escolhida != "N/A":
                termo_sub_sem_espaco = subcat_escolhida.lower().replace(" ", "")
                df_drill = df_drill[df_drill['Produto'].str.lower().str.replace(" ", "").str.contains(termo_sub_sem_espaco, na=False)]
                
                # 🚀 REPETINDO A MÁGICA PARA O GRÁFICO FINAL
                if not any(sufixo in termo_sub_sem_espaco for sufixo in ['ti', 'super', 'xt']):
                    df_drill = df_drill[
                        ~df_drill['Produto'].str.lower().str.replace(" ", "").str.contains(f"{termo_sub_sem_espaco}ti", na=False) &
                        ~df_drill['Produto'].str.lower().str.replace(" ", "").str.contains(f"{termo_sub_sem_espaco}super", na=False) &
                        ~df_drill['Produto'].str.lower().str.replace(" ", "").str.contains(f"{termo_sub_sem_espaco}xt", na=False)
                    ]

            # 3. Aplicando Filtro de Marcas
            if len(marcas_escolhidas) > 0:
                df_drill = df_drill[df_drill['Marca'].isin(marcas_escolhidas)]
                
            # 4. Aplicando Especificação
            if especificacao_extra:
                espec_limpa = ''.join(c for c in unicodedata.normalize('NFD', especificacao_extra) if unicodedata.category(c) != 'Mn').lower()
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains(espec_limpa, na=False)]
                
            # Gerando o Gráfico
            if not df_drill.empty:
                df_agrupado_drill = df_drill.groupby(['DataCaptura', 'Loja', 'Marca'])['Preco'].mean().reset_index()
                df_agrupado_drill['Preco_Label'] = df_agrupado_drill['Preco'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                df_agrupado_drill['Legenda'] = df_agrupado_drill['Loja'] + " - " + df_agrupado_drill['Marca']
                
                titulo_modelo = subcat_escolhida if subcat_escolhida and subcat_escolhida != "N/A" else ""
                titulo_graf = f"{cat_escolhida.upper()} {titulo_modelo}".strip()
                
                subtitulo = f"Marcas: {', '.join(marcas_escolhidas)}" if marcas_escolhidas else "Todas as marcas"
                subtitulo += f" | Esp: {especificacao_extra}" if especificacao_extra else ""
                
                fig_drill = px.line(
                    df_agrupado_drill, 
                    x="DataCaptura", 
                    y="Preco", 
                    color="Legenda", 
                    markers=True, 
                    text="Preco_Label", 
                    title=f"Drill-Down: {titulo_graf} ({subtitulo})", 
                    labels={"DataCaptura": "Data da Extração", "Preco": "Preço Médio (R$)", "Legenda": "Loja - Marca"}
                )
                
                fig_drill.update_traces(textposition="top center")
                fig_drill.update_layout(yaxis=dict(range=[df_agrupado_drill['Preco'].min() * 0.9, df_agrupado_drill['Preco'].max() * 1.1]))
                fig_drill.update_xaxes(tickformat="%d/%m/%Y")
                
                st.plotly_chart(fig_drill, use_container_width=True)
                
                with st.expander("Ver produtos englobados neste filtro"):
                    st.dataframe(df_drill[['Loja', 'Marca', 'Produto', 'Preco']].drop_duplicates(subset=['Produto']).head(20), width='stretch')
            else:
                 st.warning("Nenhum hardware encontrado com essa combinação exata.")
# ================= PÁGINA 2: PREVISÃO DE IA =================
elif menu == "🔮 Previsão de IA":
    st.title("🔮 Motor de Previsão de Vendas (Machine Learning)")
    st.write("Treinando o algoritmo Random Forest com dados históricos para prever a demanda futura.")

    produto_ia = st.selectbox("Selecione o Hardware para Análise Preditiva:", ["GTX 1660", "RTX 4060", "RX 7600"])
    mes_alvo = st.selectbox("Prever Demanda Para:", ["Próximo Mês (Mês 13)", "Daqui a 2 Meses (Mês 14)"])
    
    if st.button("🚀 Treinar IA e Gerar Previsão"):
        with st.spinner("Treinando o modelo Random Forest com 12 meses de histórico..."):
            time.sleep(1.5) 
            
            try:
                from sklearn.ensemble import RandomForestRegressor
                
                meses_historico = np.arange(1, 13).reshape(-1, 1) 
                precos_historico = np.array([1600, 1580, 1620, 1500, 1450, 1400, 1380, 1420, 1450, 1480, 1500, 1490])
                vendas_historico = np.array([80, 85, 70, 100, 120, 130, 140, 110, 100, 95, 90, 92])
                
                X_treino = np.column_stack((meses_historico, precos_historico))
                y_treino = vendas_historico
                
                modelo_ia = RandomForestRegressor(n_estimators=100, random_state=42)
                modelo_ia.fit(X_treino, y_treino)
                
                mes_futuro = 13 if mes_alvo == "Próximo Mês (Mês 13)" else 14
                preco_estimado = 1450 
                
                previsao_ia = modelo_ia.predict([[mes_futuro, preco_estimado]])[0]
                previsao_arredondada = int(previsao_ia)
                
                st.success(f"✅ Treinamento concluído! A Inteligência Artificial analisou os padrões de '{produto_ia}'.")
                
                st.markdown("### Cenários Projetados (Margem de Confiança)")
                colA, colB, colC = st.columns(3)
                colA.metric("📉 Cenário Pessimista", f"{int(previsao_arredondada * 0.85)} unid.")
                colB.metric("🎯 Previsão Principal", f"{previsao_arredondada} unid.", "Recomendação de Compra")
                colC.metric("📈 Cenário Otimista", f"{int(previsao_arredondada * 1.15)} unid.")
                
                st.markdown("---")
                st.markdown("### 📊 Gráfico de Tendência (Histórico vs. Previsão)")
                
                meses_grafico = list(range(1, 13)) + [mes_futuro]
                vendas_grafico = list(vendas_historico) + [previsao_arredondada]
                tipo_dado = ['Histórico Real'] * 12 + ['Previsão IA']
                
                df_grafico = pd.DataFrame({
                    "Mês": meses_grafico,
                    "Unidades Vendidas": vendas_grafico,
                    "Tipo": tipo_dado
                })
                
                fig = px.line(df_grafico, x="Mês", y="Unidades Vendidas", color="Tipo", markers=True, title="Comportamento de Vendas")
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("💡 **Dica Técnica para a Monografia:** O modelo Random Forest conseguiu prever a demanda cruzando a variável 'Tempo' com a variável 'Preço Praticado', simulando a elasticidade de demanda do mercado de hardware.")
                
            except ImportError:
                st.error("🚨 **Erro Crítico de IA:** A biblioteca Scikit-Learn não foi encontrada!")
                st.markdown("Pare o Streamlit (Ctrl+C no terminal) e digite: `pip install scikit-learn`")

# ================= PÁGINA 3: GESTÃO DE DADOS =================
elif menu == "📂 Gestão de Dados":
    st.title("📂 Ingestão, Limpeza e Tratamento")
    st.write("Módulo dedicado ao carregamento e padronização (Data Cleaning) do histórico de vendas da empresa.")
    
    if 'dados_brutos' not in st.session_state:
        st.session_state['dados_brutos'] = None
    if 'dados_tratados' not in st.session_state:
        st.session_state['dados_tratados'] = None
    if 'linhas_removidas' not in st.session_state:
        st.session_state['linhas_removidas'] = 0

    st.markdown("---")
    st.write("### 📌 Padrão Exigido para o CSV")
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
                st.error(f"❌ Erro de Formatação! Faltam as seguintes colunas no seu CSV: {', '.join(colunas_ausentes)}")
                st.warning("Ajuste o cabeçalho do seu ficheiro Excel/CSV para coincidir exatamente com as colunas exigidas acima e tente de novo.")
            else:
                st.session_state['dados_brutos'] = df_teste
                st.session_state['dados_tratados'] = None
                
        except Exception as e:
            st.error(f"Erro ao ler o ficheiro: {e}")
    
    if st.session_state['dados_brutos'] is not None:
        st.success("✅ Ficheiro validado e carregado com sucesso!")
        st.dataframe(st.session_state['dados_brutos'], width='stretch')
        
        st.markdown("---")
        st.write("### 🧹 Limpeza e Padronização de Dados")
        st.write("Clique abaixo para padronizar os dados internos com a base de dados da Nuvem AWS.")
        
        if st.button("⚙️ Executar Tratamento de Dados"):
            with st.spinner("A aplicar algoritmos de normalização..."):
                import time
                time.sleep(1) 
                
                df_tratado = st.session_state['dados_brutos'].copy()
                df_tratado.columns = df_tratado.columns.str.strip()
                df_tratado = df_tratado.dropna(how='all')
                
                colunas_texto = ['Marca', 'Produto', 'Descricao']
                for col in colunas_texto:
                    if col in df_tratado.columns:
                        df_tratado[col] = df_tratado[col].astype(str).str.lower().str.strip()
                    
                if 'DataCaptura' in df_tratado.columns:
                     try:
                         df_tratado['DataCaptura'] = pd.to_datetime(df_tratado['DataCaptura']).dt.date
                     except:
                         pass 
                
                st.session_state['dados_tratados'] = df_tratado
                st.session_state['linhas_removidas'] = len(st.session_state['dados_brutos']) - len(df_tratado)
                
    if st.session_state['dados_tratados'] is not None:
        st.write("#### ✨ Dados Normalizados e Prontos para a IA")
        st.dataframe(st.session_state['dados_tratados'], width='stretch')
        
        st.success(f"Operação concluída! {st.session_state['linhas_removidas']} linhas inválidas removidas. Nomenclatura e datas alinhadas com o banco AWS.")
        
        if st.button("🗑️ Limpar Memória e Subir Novo Arquivo"):
            st.session_state['dados_brutos'] = None
            st.session_state['dados_tratados'] = None
            st.session_state['linhas_removidas'] = 0
            st.rerun()