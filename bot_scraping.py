import pandas as pd
from datetime import datetime
import time

# As novas bibliotecas da Cavalaria Pesada
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def raspar_busca_kabum(termo_busca):
    print(f"🤖 Iniciando o Scanner de Mercado (Modo Selenium) para: '{termo_busca}'")
    
    termo_formatado = termo_busca.replace(" ", "-").lower()
    url_busca = f"https://www.kabum.com.br/busca/{termo_formatado}"
    
    # 1. Configurando o "Piloto Automático" do Chrome
    opcoes = Options()
    # Se quiser que o robô rode escondido no futuro, é só descomentar a linha abaixo:
    # opcoes.add_argument("--headless") 
    opcoes.add_argument("--disable-gpu")
    opcoes.add_argument("--window-size=1920,1080")
    
    # Instala/Abre o Chrome atualizado automaticamente
    servico = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servico, options=opcoes)
    
    try:
        # 2. O Robô entra no site de verdade
        navegador.get(url_busca)
        
        # 3. Esperamos 3 segundos para dar tempo do JavaScript da Kabum carregar os preços
        print("⏳ Aguardando o JavaScript da página carregar os preços...")
        time.sleep(3)
        
        # 4. Agora sim, com a página carregada, buscamos as classes que você descobriu!
        nomes_elementos = navegador.find_elements(By.CLASS_NAME, 'nameCard')
        precos_elementos = navegador.find_elements(By.CLASS_NAME, 'priceCard')
        
        print(f"🔍 Encontrados {len(nomes_elementos)} nomes e {len(precos_elementos)} preços na página!")
        
        lista_produtos = []
        
        # Cruza os dados extraídos
        for nome_el, preco_el in zip(nomes_elementos, precos_elementos):
            nome_limpo = nome_el.text.strip()
            preco_texto = preco_el.text.strip()
            
            if "R$" in preco_texto:
                preco_limpo = preco_texto.replace('R$', '').replace('\xa0', '').replace(' ', '').replace('.', '').replace(',', '.')
                
                try:
                    preco_float = float(preco_limpo)
                    lista_produtos.append({
                        "Produto": nome_limpo,
                        "Preço (R$)": preco_float
                    })
                except:
                    pass

        data_coleta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 5. Fecha o navegador sozinho
        navegador.quit()
        
        if len(lista_produtos) > 0:
            df_resultados = pd.DataFrame(lista_produtos)
            return {
                "data": data_coleta,
                "total_encontrados": len(lista_produtos),
                "preco_minimo": df_resultados["Preço (R$)"].min(),
                "preco_medio": df_resultados["Preço (R$)"].mean(),
                "dados_completos": df_resultados,
                "status": "Sucesso"
            }
        else:
            print("❌ O robô abriu a página, mas a lista de cruzamento ficou vazia.")
            return None

    except Exception as e:
        print(f"❌ Erro crítico no robô Selenium: {e}")
        navegador.quit()
        return None