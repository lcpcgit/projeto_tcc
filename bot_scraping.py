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
    print(f"🤖 INICIANDO MEGA-SCANNER (ALTA PROFUNDIDADE) PARA: '{termo_busca}'")
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
            marcas = [
                'cooler master', 'deepcool', 'noctua', 'scythe', 'gamdias', 'pure power', 'ryvel', 'nzxt', 'lian li',
                'seagate', 'toshiba', 'western digital', 'wd', 'sandisk', 'lacie', 'hitachi', 'hgst', 'aitek',
                'hawking', 'alltek', 'win memory', 'win memmory', 
                'razer', 'logitech', 'hyperx', 'steelseries', 'wooting', 'akko', 'epomaker', 'machenike', 'motospeed', 
                'aula', 'keychron', 'fallen', 'dazz', 'maxprint', 'bright', 'multilaser', 'multi', 'oex', 'rapoo', 'evus', 'newlink',
                'attack shark', 'mchose', 't-dagger', 'force one', 'bloody', 'intelbras', 'elg', 'exbom', 'trust', 'gxtrust', 
                'lecoo', 'neologic', '8bitdo', 'keytime', 'keyceo', 'c3tch', 'kross elegance',
                'lg', 'aoc', 'samsung', 'acer', 'philips', 'benq', 'zowie', 'hayom', '3green', 'ultra flick', 'ezviz', 'vx pro', 'pcfort',
                'geil', 'crucial', 'adata', 'lexar', 'g.skill', 'gskill', 'team group', 'teamgroup',
                'patriot', 'netac', 'oloy', 'asgard', 'hikvision', 'hiksemi', 'tob computers', 'westgatte',
                'kingston', 'corsair', 'xpg', 'husky', 'rise mode', 'mancer', 'sk hynix', 'hynix', 
                'kingspec', 'oxy', 'keepdata', 'up gamer', 'upgamer', 'diamond',
                'dell', 'hp', 'lenovo', 'ibm', 
                'asus', 'gigabyte', 'msi', 'galax', 'zotac', 'pny', 'asrock', 'sapphire', 'powercolor', 
                'ninja', 'inno3d', 'palit', 'gainward', 
                'xfx', 'evga', 'pcyes', 'colorful', 'biostar', 'yeston',
                'thermaltake', 'tt', 'gamemax', 'aerocool', 'c3tech', 'draxen', 'cowboy',
                'redragon', 'superframe', 'cougar', 'seasonic', 'onepower', 'duex', 'dxmo',
                'brx', 'tgt', 'mymax', 'fortrek', 'brazilpc', 'brazil pc', 'mach1', 'sate',
                'storm-z', 'montech', 'ktrok', 'ps-g', 'liketec', 'hyte', 'hyrax', 'kalkan', 'dr. office',
                'vinik', 'knup', 'bluecase', 'k-mex', 'kmex', 'primetek', 'concórdia', 'concordia',
                'amd', 'intel' 
            ]
            
            nome_lower = nome.lower()
            for marca in marcas:
                if re.search(rf'\b{re.escape(marca)}\b', nome_lower) or (marca == 'dxmo' and 'dxmo' in nome_lower) or (marca == 'dxmo' and ', dx' in nome_lower):
                    if marca == 'inno3d': return 'Inno3D'
                    if marca == 'pcyes': return 'PCYes'
                    if marca == 'yeston': return 'Yeston'
                    if marca == 'xfx': return 'XFX'
                    if marca == 'pny': return 'PNY'
                    if marca == 'amd': return 'AMD'
                    if marca == 'msi': return 'MSI'
                    if marca == 'evga': return 'EVGA'
                    if marca == 'c3tech' or marca == 'ps-g' or marca == 'c3tch': return 'C3Tech'
                    if marca == 'cooler master': return 'Cooler Master'
                    if marca == 'superframe': return 'SuperFrame'
                    if marca == 'xpg': return 'XPG'
                    if marca == 'onepower': return 'OnePower'
                    if marca == 'brx': return 'BRX'
                    if marca == 'tgt': return 'TGT'
                    if marca == 'mymax': return 'Mymax'
                    if marca == 'brazilpc' or marca == 'brazil pc': return 'BrazilPC'
                    if marca == 'mach1': return 'MACH1'
                    if marca == 'rise mode': return 'Rise Mode'
                    if marca == 'fortrek': return 'Fortrek'
                    if marca == 'nzxt': return 'NZXT'
                    if marca == 'lian li': return 'Lian Li'
                    if marca == 'storm-z': return 'Storm-Z'
                    if marca == 'montech': return 'Montech'
                    if marca == 'ktrok': return 'Ktrok'
                    if marca == 'thermaltake' or marca == 'tt': return 'Thermaltake'
                    if marca == 'k-mex' or marca == 'kmex': return 'K-mex'
                    if marca == 'concórdia' or marca == 'concordia': return 'Concórdia'
                    if marca == 'g.skill' or marca == 'gskill': return 'G.Skill'
                    if marca == 'team group' or marca == 'teamgroup': return 'Team Group'
                    if marca == 'sk hynix' or marca == 'hynix': return 'SK Hynix'
                    if marca == 'up gamer' or marca == 'upgamer': return 'Up Gamer'
                    if marca == 'hp': return 'HP'
                    if marca == 'ibm': return 'IBM'
                    if marca == 'dell': return 'Dell'
                    if marca == 'kingspec': return 'KingSpec'
                    if marca == 'oxy': return 'Oxy'
                    if marca == 'keepdata': return 'Keepdata'
                    if marca == 'wd' or marca == 'western digital': return 'WD'
                    if marca == 'lg': return 'LG'
                    if marca == 'aoc': return 'AOC'
                    if marca == 'zowie': return 'Zowie'
                    if marca == 'vx pro': return 'VX PRO'
                    if marca == 'pcfort': return 'PCFort'
                    if marca == 'win memory' or marca == 'win memmory': return 'Win Memory'
                    if marca == 'deepcool': return 'DeepCool'
                    if marca == 'pure power': return 'Pure Power'
                    if marca == 'ryvel': return 'Ryvel'
                    if marca == 'gamdias': return 'Gamdias'
                    if marca == 'liketec': return 'Liketec'
                    if marca == 'hyte': return 'Hyte'
                    if marca == 'hyrax': return 'Hyrax'
                    if marca == 'kalkan': return 'Kalkan'
                    if marca == 'dr. office': return 'Dr. Office'
                    if marca == 'hyperx': return 'HyperX'
                    if marca == 'steelseries': return 'SteelSeries'
                    if marca == 'logitech': return 'Logitech'
                    if marca == 'razer': return 'Razer'
                    if marca == 'machenike': return 'Machenike'
                    if marca == 'motospeed': return 'Motospeed'
                    if marca == 'epomaker': return 'Epomaker'
                    if marca == 'multilaser' or marca == 'multi': return 'Multilaser'
                    if marca == 'attack shark': return 'Attack Shark'
                    if marca == 'mchose': return 'MCHOSE'
                    if marca == 't-dagger': return 'T-Dagger'
                    if marca == 'force one': return 'Force One'
                    if marca == 'bloody': return 'Bloody'
                    if marca == 'intelbras': return 'Intelbras'
                    if marca == 'elg': return 'ELG'
                    if marca == 'exbom': return 'Exbom'
                    if marca == 'trust' or marca == 'gxtrust': return 'Trust'
                    if marca == 'lecoo': return 'Lecoo'
                    if marca == 'neologic': return 'Neologic'
                    if marca == '8bitdo': return '8BitDo'
                    if marca == 'keytime' or marca == 'keyceo': return 'Keytime'
                    if marca == 'duex' or marca == 'dxmo': return 'Duex'
                    return marca.strip().capitalize() 
            
            return "Outra/Genérica"
        
        def remover_acentos(texto):
            texto_sem_acento = ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn')
            return texto_sem_acento.lower()
        
        def produto_eh_valido(nome_produto, termo):
            nome_limpo = remover_acentos(nome_produto)
            termo_limpo = remover_acentos(termo)
            
            if re.search(r'\b(open box|recondicionado|usado|refurbished|salvado)\b', nome_limpo):
                return False

            correcoes = {
                'processadores': 'processador',
                'placas': 'placa',
                'fontes': 'fonte',
                'memorias': 'memoria',
                'gabinetes': 'gabinete',
                'coolers': 'cooler',
                'teclados': 'teclado',
                'mouses': 'mouse',
                'mauses': 'mouse',
                'mause': 'mouse',
                'monitores': 'monitor',
                'fans': 'fan'
            }
            for errado, certo in correcoes.items():
                termo_limpo = re.sub(rf'\b{errado}\b', certo, termo_limpo)
            
            buscando_pc = re.search(r'\bpc\b', termo_limpo) or 'computador' in termo_limpo or 'desktop' in termo_limpo
            if not buscando_pc:
                if re.search(r'\bpc\b', nome_limpo) or 'computador' in nome_limpo or 'desktop' in nome_limpo or 'ilha' in nome_limpo or 'workstation' in nome_limpo or 'setup' in nome_limpo: return False
            
            if 'mouse' in termo_limpo:
                if 'mousepad' in nome_limpo or 'mouse pad' in nome_limpo or 'bungee' in nome_limpo or 'grip tape' in nome_limpo or 'skate' in nome_limpo or 'feet' in nome_limpo:
                    return False
            
            if 'monitor' in termo_limpo or 'tela' in termo_limpo:
                if 'suporte' in nome_limpo or 'braco' in nome_limpo or 'articulado' in nome_limpo or 'pistao' in nome_limpo or 'barra de led' in nome_limpo or 'limpeza' in nome_limpo:
                    return False
            
            if 'teclado' in termo_limpo:
                if 'keycap' in nome_limpo or 'switch ' in nome_limpo or 'apoio' in nome_limpo or 'mousepad' in nome_limpo or 'adesivo' in nome_limpo or 'lubrificante' in nome_limpo:
                    return False
                
            if 'cabo' in nome_limpo or 'adaptador' in nome_limpo: return False
            
            if 'gabinete' in termo_limpo:
                if 'suporte' in nome_limpo or 'fita' in nome_limpo or 'controladora' in nome_limpo or 'hub' in nome_limpo or 'cabo' in nome_limpo:
                    return False
            
            if 'ssd' in termo_limpo or 'nvme' in termo_limpo or 'm.2' in termo_limpo:
                if 'gaveta' in nome_limpo or 'case' in nome_limpo or 'dissipador' in nome_limpo or 'enclosure' in nome_limpo:
                    return False
            
            if re.search(r'\bhd\b', termo_limpo) or 'ssd' in termo_limpo or 'disco' in termo_limpo or 'armazenamento' in termo_limpo:
                if 'monitor ' in nome_limpo or 'tela ' in nome_limpo or 'webcam' in nome_limpo or 'camera' in nome_limpo or 'smart tv' in nome_limpo or 'televisao' in nome_limpo:
                    return False
            
            if 'memoria' in termo_limpo or 'ram' in termo_limpo or 'ddr' in termo_limpo:
                if 'processador' in nome_limpo or 'storage' in nome_limpo or re.search(r'\bnas\b', nome_limpo) or 'servidor' in nome_limpo: 
                    return False
            
            if 'placa-mae' not in termo_limpo and 'placa mae' not in termo_limpo and 'motherboard' not in termo_limpo:
                if 'placa-mae' in nome_limpo or 'placa mae' in nome_limpo or 'motherboard' in nome_limpo or 'mainboard' in nome_limpo: return False
            
            if 'gabinete' not in termo_limpo and 'cpu' not in termo_limpo and 'processador' not in termo_limpo:
                if nome_limpo.startswith('gabinete'): return False
                if nome_limpo.startswith('processador'): return False
            
            if 'cooler' not in termo_limpo and 'water' not in termo_limpo and 'fan' not in termo_limpo:
                if nome_limpo.startswith('cooler ') or nome_limpo.startswith('water ') or nome_limpo.startswith('fan '): return False
                if 'cooler para' in nome_limpo or 'cooler processador' in nome_limpo or 'water cooler' in nome_limpo or 'watercooler' in nome_limpo: return False
                if 'ventoinha' in nome_limpo or 'dissipador' in nome_limpo: return False
            
            if 'notebook' in nome_limpo or 'laptop' in nome_limpo or 'book' in nome_limpo or 'tela' in nome_limpo: return False
            if 'kit' in nome_limpo or 'combo' in nome_limpo or 'upgrade' in nome_limpo: return False
            
            if 'enterprise' in nome_limpo or 'servidor' in nome_limpo or 'server' in nome_limpo: return False
            
            if 'super' not in termo_limpo and re.search(r'\bsuper\b', nome_limpo): return False
            if 'ti' not in termo_limpo and re.search(r'\bti\b', nome_limpo): return False
            if 'xt' not in termo_limpo and re.search(r'\bxt\b', nome_limpo): return False
            if 'xtx' not in termo_limpo and re.search(r'\bxtx\b', nome_limpo): return False
                
            palavras_da_busca = termo_limpo.split()
            for palavra in palavras_da_busca:
                if palavra.isdigit():
                    if not re.search(rf'(?<!\d){palavra}(?!\d)', nome_limpo):
                        return False
                else:
                    if palavra not in nome_limpo:
                        return False
            return True
            
        data_atual = datetime.now().strftime("%Y-%m-%d") 
        
        # ================= 1. RASPANDO A KABUM =================
        try:
            for pagina in range(1, 6):  
                url_kabum = f"https://www.kabum.com.br/busca/{termo_busca.replace(' ', '-').lower()}?page_number={pagina}&page_size=20"
                navegador.get(url_kabum)
                time.sleep(4) 
                
                nomes_kabum = navegador.find_elements(By.CSS_SELECTOR, 'span.line-clamp-2.text-ellipsis')
                precos_kabum = navegador.find_elements(By.XPATH, '//span[text()="R$"]/..')
                
                if len(nomes_kabum) == 0: break
                
                for nome_el, preco_el in zip(nomes_kabum, precos_kabum):
                    nome_completo = nome_el.get_attribute('textContent').strip()
                    if not produto_eh_valido(nome_completo, termo_busca): continue
                    
                    preco_texto = preco_el.get_attribute('textContent')
                    match = re.search(r'R\$?\s*([\d\.]+,\d{2})', preco_texto)
                    
                    if match:
                        preco_limpo = match.group(1).replace('.', '').replace(',', '.')
                        marca = extrair_marca(nome_completo)
                        
                        # 🚨 CÓDIGO NOVO: Separador de Produto e Descrição
                        partes_nome = re.split(r',\s*|;\s*|\s+-\s+', nome_completo, maxsplit=1)
                        nome_curto = partes_nome[0].strip()
                        descricao = partes_nome[1].strip() if len(partes_nome) > 1 else ""
                        
                        try: lista_produtos.append({
                            "Data": data_atual, 
                            "Loja": "Kabum",
                            "Marca": marca,
                            "Produto": nome_curto,          # Aqui entra o nome principal (ex: Ryzen 3 3200G)
                            "Descrição": descricao,         # Aqui entra as especificações
                            "Preço (R$)": float(preco_limpo)
                        })
                        except: pass
        except: pass

        # ================= 2. RASPANDO A TERABYTE =================
        try:
            url_terabyte = f"https://www.terabyteshop.com.br/busca?str={termo_busca.replace(' ', '+')}"
            navegador.get(url_terabyte)
            time.sleep(5) 
            
            for _ in range(10):
                navegador.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1)
            
            nomes_tera = navegador.find_elements(By.CSS_SELECTOR, '.product-item__name')
            precos_tera = navegador.find_elements(By.CSS_SELECTOR, '.product-item__new-price')
            
            for nome_el, preco_el in zip(nomes_tera, precos_tera):
                nome_completo = nome_el.get_attribute('textContent').strip()
                if not produto_eh_valido(nome_completo, termo_busca): continue
                    
                preco_texto = preco_el.get_attribute('textContent')
                numeros_e_virgula = re.sub(r'[^\d,]', '', preco_texto)
                
                if numeros_e_virgula:
                    preco_limpo = numeros_e_virgula.replace(',', '.')
                    marca = extrair_marca(nome_completo)
                    
                    # 🚨 CÓDIGO NOVO: Separador de Produto e Descrição
                    partes_nome = re.split(r',\s*|;\s*|\s+-\s+', nome_completo, maxsplit=1)
                    nome_curto = partes_nome[0].strip()
                    descricao = partes_nome[1].strip() if len(partes_nome) > 1 else ""
                    
                    try: lista_produtos.append({
                        "Data": data_atual, 
                        "Loja": "Terabyte",
                        "Marca": marca,
                        "Produto": nome_curto,          # Aqui entra o nome principal 
                        "Descrição": descricao,         # Aqui entra as especificações
                        "Preço (R$)": float(preco_limpo)
                    })
                    except: pass
        except: pass

        navegador.quit()
        
        if len(lista_produtos) > 0:
            df_resultados = pd.DataFrame(lista_produtos)
            
            # 🚨 CÓDIGO NOVO: Agora remove duplicados comparando Produto + Descrição para não apagar tamanhos/versões diferentes!
            df_resultados = df_resultados.drop_duplicates(subset=['Loja', 'Produto', 'Descrição'], keep='first')
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
        print(f"Erro crítico no WebDriver: {e}")
        traceback.print_exc()
        return None