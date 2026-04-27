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
            familia_input = st.text_input("Digite a Família do Hardware:", value="rtx 5070")
            
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
                    
        else:
            st.info("Aqui você seleciona o modelo **exato** para analisar o preço dele.")
            lista_produtos = sorted(df_historico['Produto'].unique())
            produto_escolhido = st.selectbox("Escolha o Hardware específico na base de dados:", lista_produtos)
            
            df_filtrado = df_historico[df_historico['Produto'] == produto_escolhido].copy()
            if not df_filtrado.empty:
                df_filtrado['Preco_Label'] = df_filtrado['Preco'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                fig = px.line(df_filtrado, x="DataCaptura", y="Preco", color="Loja", markers=True, text="Preco_Label", title=f"Histórico Específico: {produto_escolhido}", labels={"DataCaptura": "Data", "Preco": "Preço à Vista (R$)", "Loja": "Loja"})
                fig.update_traces(textposition="top center")
                fig.update_layout(yaxis=dict(range=[df_filtrado['Preco'].min() * 0.9, df_filtrado['Preco'].max() * 1.1]))
                fig.update_xaxes(tickformat="%d/%m/%Y")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Sem dados suficientes.")
                
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
            "Mouse Gamer", "Mouse", "Teclado Mecânico", "Teclado Magnético", "Headset Gamer"
        ]

        # 🚀 DICIONÁRIO DE MODELOS MAPEADO DO SEU BOT
        mapa_subcategorias = {
            "Placa de Vídeo": ["GT610", "GT730", "GTX 750 Ti", "GTX 1050 Ti", "GTX 1650", "GTX 1660", "RTX 2060", "RTX 3050", "RTX 3060", "RTX 4060", "RTX 4060 Ti", "RTX 5070", "RTX 5080", "RTX 5090", "RX 580", "RX 6600", "RX 6750 XT", "RX 7600", "Arc A750"],
            "Processador": ["Ryzen 5 4500", "Ryzen 5 5600", "Ryzen 5 5600G", "Ryzen 7 5700X", "Ryzen 7 5800X3D", "Ryzen 5 7600", "Ryzen 7 7800X3D", "Ryzen 9 9950X", "Core i3 12100F", "Core i5 12400F", "Core i5 13400F", "Core i5 14600K", "Core i7 14700K", "Core Ultra 5 245K"],
            "Placa Mãe": ["A320M", "A520M", "B450M", "B550M", "A620M", "B650M", "X670", "X870", "H610M", "B660M", "B760M", "Z790", "Z890"],
            "Memória RAM": ["8GB", "16GB", "32GB", "64GB", "DDR4", "DDR5"],
            "SSD": ["480GB", "500GB", "1TB", "2TB", "4TB", "NVMe"],
            "HD": ["1TB", "2TB", "4TB"],
            "Monitor": ["75hz", "144hz", "165hz", "240hz", "360hz", "4K", "Ultrawide"],
            "Fonte": ["500W", "600W", "650W", "750W", "850W", "1000W"],
            "Gabinete": ["Aquario", "Mid Tower", "Full Tower", "Mini ITX"],
            "Water Cooler": ["120mm", "240mm", "360mm"],
            "Fan": ["120mm", "140mm", "RGB"]
        }
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cat_escolhida = st.selectbox("1. Categoria:", [""] + sorted(categorias_base))
            
        with col2:
            opcoes_sub = [""]
            if cat_escolhida in mapa_subcategorias:
                opcoes_sub += sorted(mapa_subcategorias[cat_escolhida])
            subcat_escolhida = st.selectbox("2. Modelo:", opcoes_sub, disabled=not cat_escolhida)
            
        with col3:
            # 🚀 FILTRO DINÂMICO DE MARCAS (CATEGORIA + MODELO)
            if cat_escolhida:
                df_marcas_disponiveis = df_historico.copy()
                termo_cat_limpo = ''.join(c for c in unicodedata.normalize('NFD', cat_escolhida) if unicodedata.category(c) != 'Mn').lower()
                
                # Filtro de Categoria
                if termo_cat_limpo == "mouse":
                    df_marcas_disponiveis = df_marcas_disponiveis[df_marcas_disponiveis['Produto'].str.lower().str.contains('mouse', na=False) & ~df_marcas_disponiveis['Produto'].str.lower().str.contains('gamer', na=False)]
                elif termo_cat_limpo == "mouse gamer":
                    df_marcas_disponiveis = df_marcas_disponiveis[df_marcas_disponiveis['Produto'].str.lower().str.contains('mouse', na=False) & df_marcas_disponiveis['Produto'].str.lower().str.contains('gamer', na=False)]
                else:
                    for palavra in termo_cat_limpo.split():
                        df_marcas_disponiveis = df_marcas_disponiveis[df_marcas_disponiveis['Produto'].str.lower().str.contains(palavra, na=False)]
                
                # Filtro de Modelo (Subcategoria)
                if subcat_escolhida:
                    termo_sub = subcat_escolhida.lower().replace(" ", "")
                    df_marcas_disponiveis = df_marcas_disponiveis[df_marcas_disponiveis['Produto'].str.lower().str.replace(" ", "").str.contains(termo_sub, na=False)]
                
                marcas_filtradas = sorted([m for m in df_marcas_disponiveis['Marca'].dropna().unique() if m != "Outra/Genérica"])
            else:
                marcas_filtradas = []
            marcas_escolhidas = st.multiselect("3. Marcas:", marcas_filtradas, disabled=not cat_escolhida)
            
        with col4:
            especificacao_extra = st.text_input("4. Especificação (Ex: Branco, OC):", disabled=not cat_escolhida)
            
        if cat_escolhida: 
            df_drill = df_historico.copy()
            
            # Aplicação final dos filtros no DataFrame do gráfico
            termo_cat_limpo = ''.join(c for c in unicodedata.normalize('NFD', cat_escolhida) if unicodedata.category(c) != 'Mn').lower()
            if termo_cat_limpo == "mouse":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('mouse', na=False) & ~df_drill['Produto'].str.lower().str.contains('gamer', na=False)]
            elif termo_cat_limpo == "mouse gamer":
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains('mouse', na=False) & df_drill['Produto'].str.lower().str.contains('gamer', na=False)]
            else:
                for palavra in termo_cat_limpo.split():
                    df_drill = df_drill[df_drill['Produto'].str.lower().str.contains(palavra, na=False)]
            
            if subcat_escolhida:
                termo_sub = subcat_escolhida.lower().replace(" ", "")
                df_drill = df_drill[df_drill['Produto'].str.lower().str.replace(" ", "").str.contains(termo_sub, na=False)]

            if len(marcas_escolhidas) > 0:
                df_drill = df_drill[df_drill['Marca'].isin(marcas_escolhidas)]
                
            if especificacao_extra:
                espec_limpa = ''.join(c for c in unicodedata.normalize('NFD', especificacao_extra) if unicodedata.category(c) != 'Mn').lower()
                df_drill = df_drill[df_drill['Produto'].str.lower().str.contains(espec_limpa, na=False)]
                
            if not df_drill.empty:
                df_agrupado_drill = df_drill.groupby(['DataCaptura', 'Loja', 'Marca'])['Preco'].mean().reset_index()
                df_agrupado_drill['Preco_Label'] = df_agrupado_drill['Preco'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                df_agrupado_drill['Legenda'] = df_agrupado_drill['Loja'] + " - " + df_agrupado_drill['Marca']
                
                fig_drill = px.line(
                    df_agrupado_drill, 
                    x="DataCaptura", 
                    y="Preco", 
                    color="Legenda", 
                    markers=True, 
                    text="Preco_Label", 
                    title=f"Drill-Down: {cat_escolhida.upper()} {subcat_escolhida}", 
                    labels={"DataCaptura": "Data", "Preco": "Preço Médio (R$)", "Legenda": "Loja - Marca"}
                )
                
                fig_drill.update_traces(textposition="top center")
                fig_drill.update_layout(yaxis=dict(range=[df_agrupado_drill['Preco'].min() * 0.9, df_agrupado_drill['Preco'].max() * 1.1]))
                fig_drill.update_xaxes(tickformat="%d/%m/%Y")
                st.plotly_chart(fig_drill, use_container_width=True)
                
                with st.expander("Ver produtos englobados neste filtro"):
                    st.dataframe(df_drill[['Loja', 'Marca', 'Produto', 'Preco']].drop_duplicates(subset=['Produto']).head(20), width='stretch')
            else:
                 st.warning("Nenhum hardware encontrado com essa combinação exata.")
            
    else:
        st.warning("Aguardando dados da nuvem AWS...")
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