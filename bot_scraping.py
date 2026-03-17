import pandas as pd
from datetime import datetime
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import traceback

def escanear_mercado_completo(termo_busca):
    print(f"\n==================================================")
    print(f"🤖 INICIANDO SCANNER SUPER FILTRADO PARA: '{termo_busca}'")
    print(f"==================================================")
    
    try:
        opcoes = Options()
        opcoes.add_argument("--disable-gpu")
        opcoes.add_argument("--window-size=1920,1080")
        opcoes.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        servico = Service(ChromeDriverManager().install())
        navegador = webdriver.Chrome(service=servico, options=opcoes)
        
        lista_produtos = []
        
        def produto_eh_valido(nome_produto, termo):
            nome_lower = nome_produto.lower()
            termo_lower = termo.lower()
            
            # Bloqueios antigos
            if re.search(r'\bpc\b', nome_lower) or 'computador' in nome_lower: return False
            if 'placa mãe' in nome_lower or 'placa-mãe' in nome_lower or 'motherboard' in nome_lower: return False
            if 'cabo' in nome_lower or 'adaptador' in nome_lower or 'watercooler' in nome_lower: return False
            
            # 🚫 O NOVO BLOQUEIO: Adeus, Notebooks!
            if 'notebook' in nome_lower or 'laptop' in nome_lower: return False
                
            palavras_da_busca = termo_lower.split()
            for palavra in palavras_da_busca:
                if palavra not in nome_lower:
                    return False
            return True
            
        # ================= 1. RASPANDO A KABUM =================
        try:
            url_kabum = f"https://www.kabum.com.br/busca/{termo_busca.replace(' ', '-').lower()}"
            navegador.get(url_kabum)
            
            # Aumentei um pouco o tempo aqui só por segurança contra o Cloudflare
            time.sleep(5)
            
            # 🚨 A MUDANÇA ESTÁ AQUI: Os novos seletores baseados no Tailwind CSS
            nomes_kabum = navegador.find_elements(By.CSS_SELECTOR, 'span.line-clamp-2.text-ellipsis')
            precos_kabum = navegador.find_elements(By.XPATH, '//span[text()="R$"]/..')
            
            for nome_el, preco_el in zip(nomes_kabum, precos_kabum):
                nome = nome_el.get_attribute('textContent').strip()
                if not produto_eh_valido(nome, termo_busca): continue
                
                preco_texto = preco_el.get_attribute('textContent')
                
                # 🚨 A MUDANÇA ESTÁ AQUI: Regex ajustado para a nova forma de preço (R$1.500,00)
                match = re.search(r'R\$?\s*([\d\.]+,\d{2})', preco_texto)
                
                if match:
                    preco_limpo = match.group(1).replace('.', '').replace(',', '.')
                    try: lista_produtos.append({"Loja": "Kabum 🥷", "Produto": nome, "Preço (R$)": float(preco_limpo)})
                    except: pass
        except: pass

        # ================= 2. RASPANDO A TERABYTE =================
        try:
            url_terabyte = f"https://www.terabyteshop.com.br/busca?str={termo_busca.replace(' ', '+')}"
            navegador.get(url_terabyte)
            time.sleep(6) 
            
            # A Terabyte não mudou, então o seu código continua idêntico aqui
            nomes_tera = navegador.find_elements(By.CSS_SELECTOR, '.product-item__name')
            precos_tera = navegador.find_elements(By.CSS_SELECTOR, '.product-item__new-price')
            
            for nome_el, preco_el in zip(nomes_tera, precos_tera):
                nome = nome_el.get_attribute('textContent').strip()
                if not produto_eh_valido(nome, termo_busca): continue
                    
                preco_texto = preco_el.get_attribute('textContent')
                numeros_e_virgula = re.sub(r'[^\d,]', '', preco_texto)
                
                if numeros_e_virgula:
                    preco_limpo = numeros_e_virgula.replace(',', '.')
                    try: lista_produtos.append({"Loja": "Terabyte 🦖", "Produto": nome, "Preço (R$)": float(preco_limpo)})
                    except: pass
        except: pass

        navegador.quit()
        
        if len(lista_produtos) > 0:
            df_resultados = pd.DataFrame(lista_produtos)
            df_resultados = df_resultados.sort_values(by="Preço (R$)", ascending=True).reset_index(drop=True)
            data_coleta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {
                "data": data_coleta, "total_encontrados": len(lista_produtos),
                "preco_minimo": df_resultados["Preço (R$)"].min(), "preco_medio": df_resultados["Preço (R$)"].mean(),
                "dados_completos": df_resultados, "status": "Sucesso"
            }
        return None
    except Exception as e:
        return None