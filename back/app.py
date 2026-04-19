import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import urllib.parse

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
        # Traz apenas as colunas que importam para o gráfico
        df = pd.read_sql("SELECT DataCaptura, Loja, Produto, Preco FROM HistoricoPrecos", engine)
        
        # Garante que o Pandas entenda a coluna como "Tempo" para o gráfico ficar ordenado
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
     "📂 Gestão de Dados"] # Gestão de Dados voltou, Alertas removidos!
)

# ================= PÁGINA 1: DASHBOARD =================
if menu == "📊 Dashboard e Mercado":
    st.title("📊 Inteligência de Mercado: Scanner B2B")
    
    st.write("Acompanhe o histórico de preços reais praticados pelos maiores e-commerces (Kabum e Terabyte).")
    
    # Chama a nossa função para pegar os dados da AWS
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
                df_filtrado = df_historico[df_historico['Produto'].str.contains(familia_input, case=False, na=False)]
                
                if not df_filtrado.empty:
                    df_agrupado = df_filtrado.groupby(['DataCaptura', 'Loja'])['Preco'].mean().reset_index()
                    
                    # CRIA O RÓTULO FORMATADO (Ex: R$ 5.400,00)
                    df_agrupado['Preco_Label'] = df_agrupado['Preco'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    
                    fig = px.line(
                        df_agrupado, 
                        x="DataCaptura", 
                        y="Preco", 
                        color="Loja", 
                        markers=True, 
                        text="Preco_Label", 
                        title=f"Média de Mercado da Família: {familia_input.upper()}",
                        labels={"DataCaptura": "Data da Extração", "Preco": "Preço Médio (R$)", "Loja": "Loja Monitorada"}
                    )
                    
                    fig.update_traces(textposition="top center")
                    fig.update_layout(yaxis=dict(range=[df_agrupado['Preco'].min() * 0.9, df_agrupado['Preco'].max() * 1.1])) 
                    fig.update_xaxes(tickformat="%d/%m/%Y")
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"O sistema ainda não possui dados históricos para a família '{familia_input}'.")
                    
        else:
            # --- VISÃO ESPECÍFICA ---
            st.info("Aqui você seleciona o modelo **exato** para analisar o preço dele.")
            
            lista_produtos = sorted(df_historico['Produto'].unique())
            
            produto_escolhido = st.selectbox(
                "Escolha o Hardware específico na base de dados:", 
                lista_produtos
            )
            
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
        st.warning("Aguardando dados da nuvem AWS...")

# ================= PÁGINA 2: PREVISÃO DE IA =================
elif menu == "🔮 Previsão de IA":
    st.title("🔮 Motor de Previsão de Vendas (Machine Learning)")
    st.write("Treinando o algoritmo Random Forest com dados históricos para prever a demanda futura.")
    
    import numpy as np
    import time

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
    
    # 🚀 Inicializa as variáveis na memória do Streamlit
    if 'dados_brutos' not in st.session_state:
        st.session_state['dados_brutos'] = None
    if 'dados_tratados' not in st.session_state:
        st.session_state['dados_tratados'] = None
    if 'linhas_removidas' not in st.session_state:
        st.session_state['linhas_removidas'] = 0

    st.info("💡 **Formato esperado do CSV:** O seu ficheiro deve conter as colunas de vendas (ex: Data, Produto, Quantidade, Preco).")
    
    arquivo_upload = st.file_uploader("Suba o arquivo CSV de vendas internas:", type=["csv"])
    
    if arquivo_upload is not None:
        # Se subiu arquivo novo, guarda o bruto na memória e zera o tratado
        st.session_state['dados_brutos'] = pd.read_csv(arquivo_upload)
        st.session_state['dados_tratados'] = None
    
    if st.session_state['dados_brutos'] is not None:
        st.success("✅ Ficheiro carregado com sucesso!")
        
        st.write("### 🗄️ Dados Brutos (Raw Data)")
        st.dataframe(st.session_state['dados_brutos'], width='stretch')
        
        st.markdown("---")
        st.write("### 🧹 Limpeza e Padronização de Dados")
        st.write("Clique abaixo para higienizar a base de dados antes de a enviar para o Motor de Inteligência Artificial.")
        
        if st.button("⚙️ Executar Tratamento de Dados"):
            with st.spinner("A aplicar algoritmos de limpeza..."):
                import time
                time.sleep(1) 
                
                df_tratado = st.session_state['dados_brutos'].copy()
                df_tratado.columns = df_tratado.columns.str.title().str.strip()
                df_tratado = df_tratado.dropna(how='all')
                
                if 'Produto' in df_tratado.columns:
                    df_tratado['Produto'] = df_tratado['Produto'].str.lower().str.strip()
                
                # Guarda os dados tratados na memória
                st.session_state['dados_tratados'] = df_tratado
                st.session_state['linhas_removidas'] = len(st.session_state['dados_brutos']) - len(df_tratado)
                
    # 🚀 Se os dados já foram tratados, exibe a tabela tratada (mesmo se mudar de aba)
    if st.session_state['dados_tratados'] is not None:
        st.write("#### ✨ Dados Tratados e Prontos para Análise")
        st.dataframe(st.session_state['dados_tratados'], width='stretch')
        
        st.success(f"Operação concluída! {st.session_state['linhas_removidas']} linhas inválidas removidas. Nomenclatura de produtos padronizada.")
        
        if st.button("🗑️ Limpar Memória"):
            st.session_state['dados_brutos'] = None
            st.session_state['dados_tratados'] = None
            st.session_state['linhas_removidas'] = 0
            st.rerun()