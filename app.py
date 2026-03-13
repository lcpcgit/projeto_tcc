import streamlit as st
import pandas as pd
import numpy as np

# Configuração inicial
st.set_page_config(page_title="Hardware Preditivo AI", layout="wide")

st.sidebar.title("IA Hardware B2B")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegação do Sistema:",
    ["Dashboard e Mercado", 
     "Previsão de IA", 
     "Alertas de Estoque", 
     "Gestão de Dados"]
)

if menu == "Dashboard e Mercado":
    st.title("Inteligência de Mercado: Visão Geral")
    st.write("Acompanhe o preço praticado pela nossa loja vs. o preço do mercado (Concorrentes).")
    
    # dados fictícios teste
    dados_mock = pd.DataFrame({
        'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai'],
        'Nosso Preço (RTX 4060)': [2100, 2050, 2000, 1950, 1950],
        'Preço Mercado (Ex: Kabum)': [2050, 2000, 1900, 1850, 1800]
    }).set_index('Mês')
    
    # graficos 
    st.line_chart(dados_mock)
    
    col1, col2 = st.columns(2)
    col1.metric("Vendas no Mês Atual", "145 unidades", "+5% vs mês passado")
    col2.metric("Preço Médio Praticado", "R$ 1.950,00", "-R$ 50,00 vs mercado")

# PREVISÃO 
elif menu == "Previsão de IA":
    st.title("Motor de Previsão de Demanda")
    st.write("Selecione o componente para que a Inteligência Artificial calcule a demanda do próximo mês.")
    
    produto = st.selectbox("Selecione o Hardware:", ["Placa de Vídeo RTX 4060", "Processador Intel Core i9", "Memória RAM 16GB DDR5"])
    mes_alvo = st.selectbox("Mês de Previsão:", ["Novembro/2026", "Dezembro/2026", "Janeiro/2027"])
    
    if st.button("Rodar Algoritmo Preditivo (Machine Learning)"):
        st.success(f"Análise concluída para: {produto}")
        st.write("### Resultado da IA:")
        
        #Intervalos de confiança 
        colA, colB, colC = st.columns(3)
        colA.metric("Cenário Pessimista", "120 unid.")
        colB.metric("Previsão Principal", "150 unid.")
        colC.metric("Cenário Otimista", "180 unid.")
        st.info("💡 A IA identificou que o preço do mercado está em queda, o que pode impulsionar as vendas no cenário otimista.")

# ALERTAS DO ESTOQUE
elif menu == "Alertas de Estoque":
    st.title("Alertas Inteligentes de Ruptura e Capital Parado")
    st.write("Cruzamento do estoque físico atual com as previsões da IA.")
    
    st.error("**ALERTA VERMELHO: Risco de Ruptura!**\n\n**Produto:** Processador Intel Core i9\n**Estoque Atual:** 15 unidades\n**Previsão IA (Próx. Mês):** 45 unidades\n*Ação sugerida: Comprar lote imediatamente.*")
    
    st.warning("**ALERTA AMARELO: Estoque Encalhado!**\n\n**Produto:** Placa-Mãe B550\n**Estoque Atual:** 200 unidades\n**Previsão IA (Próx. Mês):** 20 unidades\n*Ação sugerida: Realizar promoção.*")
    
    st.success("**Placa de Vídeo RTX 4060:** Estoque saudável e alinhado com a previsão.")

# GESTÃO DE DADOS 
elif menu == "Gestão de Dados":
    st.title("Ingestão, Limpeza e Tratamento")
    st.write("Faça o upload da base bruta. O sistema aplicará as regras de Data Cleaning automaticamente.")
    
    arquivo_upload = st.file_uploader("Suba o arquivo CSV de vendas internas:", type=["csv"])
    
    if arquivo_upload is not None:
        st.write("Base de dados carregada com sucesso!")
        # futuro código pandas 
        st.button("Executar Limpeza de Dados e Exportar")