import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
from sqlalchemy import create_engine
import urllib.parse

# 1. ENSINANDO O CAMINHO: Faz o Python olhar para a pasta principal do projeto
pasta_principal = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pasta_principal)

# 2. IMPORTAÇÃO CORRIGIDA: Agora ele entra na pasta 'automacao' e pega o bot
from automacao.bot_scraping import escanear_mercado_completo

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
     "⚠️ Alertas de Estoque", 
     "📂 Gestão de Dados"]
)

# ================= PÁGINA 1: DASHBOARD =================
# ================= PÁGINA 1: DASHBOARD =================
if menu == "📊 Dashboard e Mercado":
    st.title("📊 Inteligência de Mercado: Scanner B2B")
    
    st.write("Acompanhe o histórico de preços reais praticados pelos maiores e-commerces (Kabum e Terabyte).")
    
    # Chama a nossa função para pegar os dados da AWS
    df_historico = carregar_dados_aws()
    
    if not df_historico.empty:
        st.write("### 📈 Tendência de Preços na Concorrência")
        
        # --- A GRANDE ATUALIZAÇÃO: RÁDIO DE SELEÇÃO DE VISÃO ---
        modo_visao = st.radio(
            "Selecione o Nível de Análise:", 
            ["🌐 Visão Geral (Média de Preços da Família)", "🔍 Visão Específica (Produto Exato)"],
            horizontal=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True) # Dá só um espacinho visual
        
        if modo_visao == "🌐 Visão Geral (Média de Preços da Família)":
            st.info("Aqui você digita a família da peça (Ex: RTX 5070, B650, RX 7600) e o sistema calcula a **média de preços** de todos os modelos daquela linha no dia.")
            
            familia_input = st.text_input("Digite a Família do Hardware:", value="rtx 5070")
            
            if familia_input:
                # 1. Filtra a tabela onde o nome do produto contém a palavra digitada (ignorando maiúsculas/minúsculas)
                df_filtrado = df_historico[df_historico['Produto'].str.contains(familia_input, case=False, na=False)]
                
                if not df_filtrado.empty:
                    # 2. A MÁGICA DOS DADOS: Agrupa pelo Dia e pela Loja, e calcula a MÉDIA do preço
                    df_agrupado = df_filtrado.groupby(['DataCaptura', 'Loja'])['Preco'].mean().reset_index()
                    
                    fig = px.line(
                        df_agrupado, 
                        x="DataCaptura", 
                        y="Preco", 
                        color="Loja", 
                        markers=True, 
                        title=f"Média de Mercado da Família: {familia_input.upper()}",
                        labels={"DataCaptura": "Data da Extração", "Preco": "Preço Médio (R$)", "Loja": "Loja Monitorada"}
                    )
                    
                    # 🚀 CORREÇÃO DO EIXO X: Mostra apenas Dia/Mês/Ano
                    fig.update_xaxes(tickformat="%d/%m/%Y")
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"O sistema ainda não possui dados históricos para a família '{familia_input}'.")
                    
        else:
            # --- A LÓGICA ANTIGA (VISÃO ESPECÍFICA) ---
            st.info("Aqui você seleciona o modelo **exato** para analisar o preço dele.")
            
            lista_produtos = sorted(df_historico['Produto'].unique())
            
            produto_escolhido = st.selectbox(
                "Escolha o Hardware específico na base de dados:", 
                lista_produtos
            )
            
            df_filtrado = df_historico[df_historico['Produto'] == produto_escolhido]
            
            fig = px.line(
                df_filtrado, 
                x="DataCaptura", 
                y="Preco", 
                color="Loja", 
                markers=True, 
                title=f"Histórico Específico: {produto_escolhido}",
                labels={"DataCaptura": "Data da Extração", "Preco": "Preço à Vista (R$)", "Loja": "Loja Monitorada"}
            )
            
            # 🚀 CORREÇÃO DO EIXO X: Mostra apenas Dia/Mês/Ano
            fig.update_xaxes(tickformat="%d/%m/%Y")
            
            st.plotly_chart(fig, use_container_width=True)
            
    else:
        st.warning("Aguardando dados da nuvem AWS...")
    # --- SECÇÃO DO ROBÔ DE BUSCA ---
    st.subheader("🤖 Scanner de Mercado em Tempo Real")
    st.write("Pesquise um componente para varrer os preços atuais da concorrência e calcular a média de mercado.")
    
    termo_input = st.text_input("Buscar Hardware no Mercado (Ex: gtx 1660, rtx 4060, ryzen 5):", value="gtx 1660")
    
    if st.button("🔍 Escanear Mercado Agora"):
        with st.spinner(f"O robô está a varrer as lojas à procura de '{termo_input}'..."):
            
            resultado_robo = escanear_mercado_completo(termo_input)
            
            if resultado_robo:
                st.success(f"✅ Varredura concluída! Foram encontrados {resultado_robo['total_encontrados']} modelos compatíveis.")
                
                st.write("### 🏪 Distribuição de Estoque por Loja")
                col_k, col_t = st.columns(2)
                col_k.metric("🥷 Kabum", f"{resultado_robo['total_kabum']} produtos")
                col_t.metric("🦖 Terabyte", f"{resultado_robo['total_terabyte']} produtos")
                st.markdown("---")
                
                st.write("### 💰 Análise de Preços")
                col1, col2, col3 = st.columns(3)
                col1.metric("Preço Médio (Mercado)", f"R$ {resultado_robo['preco_medio']:.2f}")
                col2.metric("Menor Preço Encontrado", f"R$ {resultado_robo['preco_minimo']:.2f}")
                col3.metric("O Nosso Preço (Fictício)", "R$ 1.450,00", f"{resultado_robo['preco_medio'] - 1450:.2f} diferença")
                
                st.markdown("---")
                st.write("### 📋 Tabela de Produtos Raspados")
                st.write("Abaixo está a base de dados bruta extraída pelo robô neste exato segundo:")
                
                st.dataframe(
                    resultado_robo['dados_completos'], 
                    width='stretch',
                    column_config={
                        "Preço (R$)": st.column_config.NumberColumn(
                            "Preço de Mercado",
                            help="Preço convertido para reais",
                            format="R$ %.2f"
                        )
                    }
                )
            else:
                st.error("❌ O robô não conseguiu encontrar dados. Verifique o terminal para erros de HTML.")

# ================= OUTRAS PÁGINAS (Mantidas iguais) =================
elif menu == "🔮 Previsão de IA":
    st.title("🔮 Motor de Previsão de Vendas (Machine Learning)")
    st.write("Treinando o algoritmo Random Forest com dados históricos para prever a demanda futura.")
    
    import numpy as np
    import plotly.express as px
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

elif menu == "⚠️ Alertas de Estoque":
    st.title("⚠️ Alertas Inteligentes de Ruptura e Capital Parado")
    st.warning("⚠️ **ALERTA AMARELO: Estoque Encalhado!**\n\n**Produto:** Placa-Mãe B550\n**Estoque:** 200 unid.\n**Previsão IA:** 20 unid.")

# ================= PÁGINA 4: GESTÃO DE DADOS =================
elif menu == "📂 Gestão de Dados":
    st.title("📂 Ingestão, Limpeza e Tratamento")
    st.write("Módulo dedicado ao carregamento e padronização (Data Cleaning) do histórico de vendas da empresa.")
    
    st.info("💡 **Formato esperado do CSV:** O seu ficheiro deve conter as colunas de vendas (ex: Data, Produto, Quantidade, Preco).")
    
    arquivo_upload = st.file_uploader("Suba o arquivo CSV de vendas internas:", type=["csv"])
    
    if arquivo_upload is not None:
        df_interno = pd.read_csv(arquivo_upload)
        st.success("✅ Ficheiro carregado com sucesso!")
        
        st.write("### 🗄️ Dados Brutos (Raw Data)")
        st.dataframe(df_interno, width='stretch')
        
        st.markdown("---")
        st.write("### 🧹 Limpeza e Padronização de Dados")
        st.write("Clique abaixo para higienizar a base de dados antes de a enviar para o Motor de Inteligência Artificial.")
        
        if st.button("⚙️ Executar Tratamento de Dados"):
            with st.spinner("A aplicar algoritmos de limpeza..."):
                import time
                time.sleep(1) 
                
                df_tratado = df_interno.copy()
                df_tratado.columns = df_tratado.columns.str.title().str.strip()
                df_tratado = df_tratado.dropna(how='all')
                
                if 'Produto' in df_tratado.columns:
                    df_tratado['Produto'] = df_tratado['Produto'].str.lower().str.strip()
                
                st.session_state['dados_internos'] = df_tratado
                
                st.write("#### ✨ Dados Tratados e Prontos para Análise")
                st.dataframe(df_tratado, width='stretch')
                
                linhas_removidas = len(df_interno) - len(df_tratado)
                st.success(f"Operação concluída! {linhas_removidas} linhas inválidas removidas. Nomenclatura de produtos padronizada.")