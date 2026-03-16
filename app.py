import streamlit as st
import pandas as pd

# 1. IMPORTAÇÃO CORRIGIDA: Agora importamos a função de busca!
from bot_scraping import raspar_busca_kabum 

st.set_page_config(page_title="Hardware Preditivo AI", layout="wide")

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
if menu == "📊 Dashboard e Mercado":
    st.title("📊 Inteligência de Mercado: Scanner B2B")
    
    st.write("Acompanhe o histórico do preço praticado pela nossa loja vs. o mercado.")
    dados_mock = pd.DataFrame({
        'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai'],
        'Nosso Preço Médio': [1600, 1550, 1500, 1450, 1450],
        'Mercado (Média)': [1550, 1500, 1400, 1399, 1399]
    }).set_index('Mês')
    st.line_chart(dados_mock)
    
    st.markdown("---")
    
    # --- SECÇÃO DO ROBÔ ATUALIZADA ---
    st.subheader("🤖 Scanner de Mercado em Tempo Real")
    st.write("Pesquise um componente para varrer os preços atuais da concorrência e calcular a média de mercado.")
    
    # Novo input: agora o gestor digita apenas o nome da peça!
    termo_input = st.text_input("Buscar Hardware no Mercado (Ex: gtx 1660, rtx 4060, ryzen 5):", value="gtx 1660")
    
    if st.button("🔍 Escanear Mercado Agora"):
        with st.spinner(f"O robô está a varrer a Kabum à procura de '{termo_input}'..."):
            
            # Chama a NOVA função
            resultado_robo = raspar_busca_kabum(termo_input)
            
            if resultado_robo:
                st.success(f"✅ Varredura concluída! Foram encontrados {resultado_robo['total_encontrados']} modelos compatíveis.")
                
                # Exibindo os cálculos que o robô fez
                col1, col2, col3 = st.columns(3)
                col1.metric("Preço Médio (Mercado)", f"R$ {resultado_robo['preco_medio']:.2f}")
                col2.metric("Menor Preço Encontrado", f"R$ {resultado_robo['preco_minimo']:.2f}")
                col3.metric("O Nosso Preço (Fictício)", "R$ 1.450,00", f"{resultado_robo['preco_medio'] - 1450:.2f} diferença")
                
                st.write("### 📋 Tabela de Produtos Raspados")
                st.write("Abaixo está a base de dados bruta extraída pelo robô neste exato segundo:")
                # Plota a tabela do Pandas diretamente na tela do Streamlit!
                st.dataframe(resultado_robo['dados_completos'], use_container_width=True)
            else:
                st.error("❌ O robô não conseguiu encontrar dados. Verifique o terminal para erros de HTML.")

# ================= OUTRAS PÁGINAS (Mantidas iguais) =================
elif menu == "🔮 Previsão de IA":
    st.title("🔮 Motor de Previsão de Demanda")
    produto = st.selectbox("Selecione o Hardware:", ["Placa de Vídeo GTX 1660 Super", "Processador Intel Core i9"])
    mes_alvo = st.selectbox("Mês de Previsão:", ["Novembro/2026", "Dezembro/2026"])
    if st.button("🚀 Rodar Algoritmo"):
        st.success(f"Análise concluída para: {produto}")
        colA, colB, colC = st.columns(3)
        colA.metric("Cenário Pessimista", "120 unid.")
        colB.metric("Previsão Principal", "150 unid.")
        colC.metric("Cenário Otimista", "180 unid.")

elif menu == "⚠️ Alertas de Estoque":
    st.title("⚠️ Alertas Inteligentes de Ruptura e Capital Parado")
    st.warning("⚠️ **ALERTA AMARELO: Estoque Encalhado!**\n\n**Produto:** Placa-Mãe B550\n**Estoque:** 200 unid.\n**Previsão IA:** 20 unid.")

elif menu == "📂 Gestão de Dados":
    st.title("📂 Ingestão, Limpeza e Tratamento")
    st.file_uploader("Suba o arquivo CSV de vendas internas:", type=["csv"])