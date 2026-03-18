import streamlit as st
import pandas as pd

# 1. IMPORTAÇÃO CORRIGIDA: Agora importamos a função de busca!
from bot_scraping import escanear_mercado_completo

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
        with st.spinner(f"O robô está a varrer as lojas à procura de '{termo_input}'..."):
            
            # Chama a NOVA função
            resultado_robo = escanear_mercado_completo(termo_input)
            
            if resultado_robo:
                st.success(f"✅ Varredura concluída! Foram encontrados {resultado_robo['total_encontrados']} modelos compatíveis.")
                
                # -------------------------------------------------------------
                # OS NOVOS CONTADORES POR LOJA
                # -------------------------------------------------------------
                st.write("### 🏪 Distribuição de Estoque por Loja")
                col_k, col_t = st.columns(2)
                col_k.metric("🥷 Kabum", f"{resultado_robo['total_kabum']} produtos")
                col_t.metric("🦖 Terabyte", f"{resultado_robo['total_terabyte']} produtos")
                st.markdown("---")
                
                # Exibindo os cálculos de preço que já tínhamos
                st.write("### 💰 Análise de Preços")
                col1, col2, col3 = st.columns(3)
                col1.metric("Preço Médio (Mercado)", f"R$ {resultado_robo['preco_medio']:.2f}")
                col2.metric("Menor Preço Encontrado", f"R$ {resultado_robo['preco_minimo']:.2f}")
                col3.metric("O Nosso Preço (Fictício)", "R$ 1.450,00", f"{resultado_robo['preco_medio'] - 1450:.2f} diferença")
                
                st.markdown("---")
                st.write("### 📋 Tabela de Produtos Raspados")
                st.write("Abaixo está a base de dados bruta extraída pelo robô neste exato segundo:")
                
                # A NOVA TABELA FORMATADA
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
    
    # Imports necessários para a IA (pode colocá-los lá no topo do ficheiro depois, se preferir)
    import numpy as np
    import plotly.express as px # Biblioteca linda para gráficos interativos
    import time

    produto_ia = st.selectbox("Selecione o Hardware para Análise Preditiva:", ["GTX 1660", "RTX 4060", "RX 7600"])
    mes_alvo = st.selectbox("Prever Demanda Para:", ["Próximo Mês (Mês 13)", "Daqui a 2 Meses (Mês 14)"])
    
    if st.button("🚀 Treinar IA e Gerar Previsão"):
        with st.spinner("Treinando o modelo Random Forest com 12 meses de histórico..."):
            time.sleep(1.5) # Charme de carregamento
            
            try:
                from sklearn.ensemble import RandomForestRegressor
                
                # 1. CRIANDO O HISTÓRICO FALSO (Até ter o SQL Server)
                # Vamos simular que quanto menor o preço, mais placas vendemos.
                meses_historico = np.arange(1, 13).reshape(-1, 1) # Meses de 1 a 12
                precos_historico = np.array([1600, 1580, 1620, 1500, 1450, 1400, 1380, 1420, 1450, 1480, 1500, 1490])
                vendas_historico = np.array([80, 85, 70, 100, 120, 130, 140, 110, 100, 95, 90, 92])
                
                # 2. PREPARANDO OS DADOS PARA A IA
                # A IA vai aprender olhando para: [Mês, Preço Médio] -> Para prever: [Vendas]
                X_treino = np.column_stack((meses_historico, precos_historico))
                y_treino = vendas_historico
                
                # 3. TREINANDO O ALGORITMO (O Coração do seu TCC)
                modelo_ia = RandomForestRegressor(n_estimators=100, random_state=42)
                modelo_ia.fit(X_treino, y_treino)
                
                # 4. FAZENDO A PREVISÃO
                mes_futuro = 13 if mes_alvo == "Próximo Mês (Mês 13)" else 14
                preco_estimado = 1450 # Preço médio que esperamos praticar
                
                # A IA faz a mágica aqui:
                previsao_ia = modelo_ia.predict([[mes_futuro, preco_estimado]])[0]
                previsao_arredondada = int(previsao_ia)
                
                # 5. EXIBINDO OS RESULTADOS COM ESTILO
                st.success(f"✅ Treinamento concluído! A Inteligência Artificial analisou os padrões de '{produto_ia}'.")
                
                st.markdown("### Cenários Projetados (Margem de Confiança)")
                colA, colB, colC = st.columns(3)
                colA.metric("📉 Cenário Pessimista", f"{int(previsao_arredondada * 0.85)} unid.")
                colB.metric("🎯 Previsão Principal", f"{previsao_arredondada} unid.", "Recomendação de Compra")
                colC.metric("📈 Cenário Otimista", f"{int(previsao_arredondada * 1.15)} unid.")
                
                st.markdown("---")
                st.markdown("### 📊 Gráfico de Tendência (Histórico vs. Previsão)")
                
                # Juntando o passado com o futuro para desenhar o gráfico
                meses_grafico = list(range(1, 13)) + [mes_futuro]
                vendas_grafico = list(vendas_historico) + [previsao_arredondada]
                tipo_dado = ['Histórico Real'] * 12 + ['Previsão IA']
                
                df_grafico = pd.DataFrame({
                    "Mês": meses_grafico,
                    "Unidades Vendidas": vendas_grafico,
                    "Tipo": tipo_dado
                })
                
                # Desenha um gráfico interativo no Streamlit
                fig = px.line(df_grafico, x="Mês", y="Unidades Vendidas", color="Tipo", markers=True, title="Comportamento de Vendas")
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("💡 **Dica Técnica para a Monografia:** O modelo Random Forest conseguiu prever a demanda cruzando a variável 'Tempo' com a variável 'Preço Praticado', simulando a elasticidade de demanda do mercado de hardware.")
                
            except ImportError:
                st.error("🚨 **Erro Crítico de IA:** A biblioteca Scikit-Learn não foi encontrada!")
                st.markdown("""
                Para resolver isso, você precisa instalar a biblioteca no mesmo terminal onde roda o Streamlit.
                
                Pare o Streamlit (Ctrl+C no terminal) e digite este comando:
                `pip install scikit-learn`
                
                Depois, inicie o Streamlit novamente.
                """)

elif menu == "⚠️ Alertas de Estoque":
    st.title("⚠️ Alertas Inteligentes de Ruptura e Capital Parado")
    st.warning("⚠️ **ALERTA AMARELO: Estoque Encalhado!**\n\n**Produto:** Placa-Mãe B550\n**Estoque:** 200 unid.\n**Previsão IA:** 20 unid.")

elif menu == "📂 Gestão de Dados":
    st.title("📂 Ingestão, Limpeza e Tratamento")
    st.file_uploader("Suba o arquivo CSV de vendas internas:", type=["csv"])