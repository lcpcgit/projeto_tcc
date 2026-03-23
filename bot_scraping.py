import pandas as pd
from datetime import datetime
import time
import re
import unicodedata 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import traceback

def escanear_mercado_completo(termo_busca):
    print(f"\n==================================================")
    print(f"🤖 INICIANDO SCANNER COM PAGINAÇÃO PARA: '{termo_busca}'")
    print(f"==================================================")
    
    try:
        opcoes = Options()
        opcoes.add_argument("--disable-gpu")
        opcoes.add_argument("--window-size=1920,1080")
        opcoes.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        servico = Service(ChromeDriverManager().install())
        navegador = webdriver.Chrome(service=servico, options=opcoes)
        
        lista_produtos = []
        
        def extrair_marca(nome):
            marcas = ['asus', 'gigabyte', 'msi', 'galax', 'zotac', 'pny', 'asrock', 'sapphire', 'powercolor', 'amd', 'intel', 'corsair', 'kingston', 'husky', 'ninja', 'inno3d', 'palit', 'gainward', 'xfx', 'evga', 'pcyes', 'colorful', 'biostar']
            
            nome_lower = nome.lower()
            for marca in marcas:
                if marca in nome_lower:
                    if marca == 'inno3d': return 'Inno3D'
                    if marca == 'pcyes': return 'PCYes'
                    if marca == 'xfx': return 'XFX'
                    if marca == 'pny': return 'PNY'
                    if marca == 'amd': return 'AMD'
                    if marca == 'msi': return 'MSI'
                    if marca == 'evga': return 'EVGA'
                    return marca.capitalize() 
            
            return "Outra/Genérica"
        
        def remover_acentos(texto):
            texto_sem_acento = ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn')
            return texto_sem_acento.lower()
        
        def produto_eh_valido(nome_produto, termo):
            nome_limpo = remover_acentos(nome_produto)
            termo_limpo = remover_acentos(termo)
            
            buscando_pc = re.search(r'\bpc\b', termo_limpo) or 'computador' in termo_limpo or 'desktop' in termo_limpo
            if not buscando_pc:
                if re.search(r'\bpc\b', nome_limpo) or 'computador' in nome_limpo or 'desktop' in nome_limpo: return False
                
            if 'cabo' in nome_limpo or 'adaptador' in nome_limpo or 'watercooler' in nome_limpo: return False
            if 'notebook' in nome_limpo or 'laptop' in nome_limpo or 'book' in nome_limpo or 'tela' in nome_limpo: return False
            if 'kit' in nome_limpo or 'combo' in nome_limpo or 'upgrade' in nome_limpo: return False
                
            palavras_da_busca = termo_limpo.split()
            for palavra in palavras_da_busca:
                # 🚨 NOVA REGRA DE INTELIGÊNCIA NUMÉRICA
                # Se a palavra for apenas um número curto (ex: 3, 5, 7, 9), usa o Regex \b para garantir que ele está isolado!
                if palavra.isdigit() and len(palavra) <= 2:
                    if not re.search(rf'\b{palavra}\b', nome_limpo):
                        return False
                else:
                    if palavra not in nome_limpo:
                        return False
            return True
            
        data_atual = datetime.now().strftime("%Y-%m-%d") 
        
        # ================= 1. RASPANDO A KABUM =================
        try:
            for pagina in range(1, 4):
                url_kabum = f"https://www.kabum.com.br/busca/{termo_busca.replace(' ', '-').lower()}?page_number={pagina}"
                navegador.get(url_kabum)
                time.sleep(5) 
                
                nomes_kabum = navegador.find_elements(By.CSS_SELECTOR, 'span.line-clamp-2.text-ellipsis')
                precos_kabum = navegador.find_elements(By.XPATH, '//span[text()="R$"]/..')
                
                if len(nomes_kabum) == 0: break
                
                for nome_el, preco_el in zip(nomes_kabum, precos_kabum):
                    nome = nome_el.get_attribute('textContent').strip()
                    if not produto_eh_valido(nome, termo_busca): continue
                    
                    preco_texto = preco_el.get_attribute('textContent')
                    match = re.search(r'R\$?\s*([\d\.]+,\d{2})', preco_texto)
                    
                    if match:
                        preco_limpo = match.group(1).replace('.', '').replace(',', '.')
                        marca = extrair_marca(nome)
                        
                        try: lista_produtos.append({
                            "Data": data_atual, 
                            "Loja": "Kabum",
                            "Marca": marca,
                            "Produto": nome, 
                            "Preço (R$)": float(preco_limpo)
                        })
                        except: pass
        except: pass

        # ================= 2. RASPANDO A TERABYTE =================
        try:
            url_terabyte = f"https://www.terabyteshop.com.br/busca?str={termo_busca.replace(' ', '+')}"
            navegador.get(url_terabyte)
            time.sleep(6) 
            
            nomes_tera = navegador.find_elements(By.CSS_SELECTOR, '.product-item__name')
            precos_tera = navegador.find_elements(By.CSS_SELECTOR, '.product-item__new-price')
            
            for nome_el, preco_el in zip(nomes_tera, precos_tera):
                nome = nome_el.get_attribute('textContent').strip()
                if not produto_eh_valido(nome, termo_busca): continue
                    
                preco_texto = preco_el.get_attribute('textContent')
                numeros_e_virgula = re.sub(r'[^\d,]', '', preco_texto)
                
                if numeros_e_virgula:
                    preco_limpo = numeros_e_virgula.replace(',', '.')
                    marca = extrair_marca(nome)
                    
                    try: lista_produtos.append({
                        "Data": data_atual, 
                        "Loja": "Terabyte",
                        "Marca": marca,
                        "Produto": nome, 
                        "Preço (R$)": float(preco_limpo)
                    })
                    except: pass
        except: pass

        navegador.quit()
        
        if len(lista_produtos) > 0:
            df_resultados = pd.DataFrame(lista_produtos)
            df_resultados = df_resultados.drop_duplicates(subset=['Loja', 'Produto'], keep='first')
            df_resultados = df_resultados.sort_values(by="Preço (R$)", ascending=True).reset_index(drop=True)
            
            qtd_kabum = len(df_resultados[df_resultados['Loja'] == 'Kabum'])
            qtd_terabyte = len(df_resultados[df_resultados['Loja'] == 'Terabyte'])
            
            return {
                "total_encontrados": len(df_resultados), 
                "total_kabum": qtd_kabum,       
                "total_terabyte": qtd_terabyte, 
                "preco_minimo": df_resultados["Preço (R$)"].min(), 
                "preco_medio": df_resultados["Preço (R$)"].mean(),
                "dados_completos": df_resultados, 
            }
        return None
    except Exception as e:
        return None