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

# 🚨 CÓDIGO FINAL: Parâmetro salvar_no_banco e integração AWS ativada
def escanear_mercado_completo(termo_busca, salvar_no_banco=False):
    print(f"\n==================================================")
    print(f"🤖 INICIANDO MEGA-SCANNER PARA: '{termo_busca}'")
    print(f"💾 Salvar na Nuvem AWS: {'SIM' if salvar_no_banco else 'NÃO'}")
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
                'amd', 'intel',

                'havit', 'jbl', 'alienware', 'aiwa', 'akg', 'aigo', 'altomex',
                'antec', 'aorus', 'arctic', 'arktek', 'behringer', 'bose', 'boya',
                'coolmoon', 'creative', 'dahua', 'darkflash', 'darmoshark', 'denon',
                'dji', 'edifier', 'elgato', 'epson', 'fantech', 'fifine', 'fnatic',
                'fractal', 'fsp', 'genius', 'godox', 'goldentec', 'gradiente', 'harman', 'hewlett',
            
                'geometric future', '1stplayer', 'astro', 'klevv', 'segotep', 'tronos', 'revenger',
                'bpc', 'hoopson', 'new hero', 'macrovip', 'arzopa', 'atk', 'tomate', 'xtrike',
                'xiaomi', 'clanm', 'grasep', 'lamzu', 'audio-technica', 'esr', 'monocron',
                'ugreen', 'targus', 'shure', 'jonsbo', 'maono', 'leson', 'pcwinmax', 'winnfox',
                'peladn', 'wavlink', 'maxsun', 'ulanzi', 'hollyland', 'synco', 'sennheiser',
                'poly', 'plantronics', 'neewer', 'mamen', 'lelong', 'be quiet', 'sharkoon',
                'warrior', 'evolut', 'satellite', 'silverstone',

                'kbm! gaming', 'rode', 'xzone', 'c3-tech', 'pioneer', 'elgin', 'tcl', 'philco',
                'lexsen', 'kadosh', 'comica', 'lensgo', 'vimai', 'blue snowball', 'dukie',
                'lorben', 'zoom', 'oxybr', 'walram', 'golden memory', 'hpe', 'yealink',
                'sades', 'onikuma', 'goldenultra', 'lehmox', 'topuse', 'sony', 'panasonic',

                'afox', 'vxpro', 'dex', 'phanteks', 'akasa', 'telefunken', 'klipsch', 'mondial',
                'harmonics', 'dylan', 'streamplify', 'microsoft', 'endgame gear', 'aplus',
                'argom', 'santana', 'pixxo', 'wanptek', 'westinghouse',

                'round5', 'sevenhero', 'hq', 'axpro', 'odyssey', 'dale7', 'sansung', 'tribit', 
                'waveone', 'cmteck', 'ilectry vision', 'xlinne', 'worldview', '3geen', 'ntc', 
                'bestbattery', 'bestoss', 'wb black', 'synex', 'ioway', 'sgmax', 'king', 
                'fanxiang', 'polyvox', 'vokal', 'kaidi', 'microdigi', 'snaker', 'playshop', 
                'marvo scorpion', 'g-fire', 'joy', 'nextpc', 'gbt', 'pctop', 'mxt', 'kapbom', 
                'ebai', 'ckmova', 'mirfak', 'sairen', 'lotus', 'storm', 'csr', 'santo angelo', 
                'ajazz', 'cross do brasil', 'g-hox', 'byz', 'kaster'
                
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
                    if marca == 'jbl': return 'JBL'
                    if marca == 'akg': return 'AKG'
                    if marca == 'dji': return 'DJI'
                    if marca == 'fsp': return 'FSP'
                    if marca == 'atk': return 'ATK'
                    if marca == 'bpc': return 'BPC'
                    if marca == 'esr': return 'ESR'
                    if marca == 'be quiet': return 'Be Quiet!'
                    if marca == '1stplayer': return '1stPlayer'
                    if marca == 'audio-technica': return 'Audio-Technica'
                    if marca == 'pcwinmax': return 'PCWinmax'
                    if marca == 'plantronics': return 'Poly'
                    if marca == 'kinology': return 'Kinology'
                    if marca == 'radeon': return 'AMD'
                    if marca == 'nvidia' or marca == 'geforce' or marca == 'gforce' or marca == 'g-force': return 'NVIDIA'
                    if marca == 'afox': return 'AFOX'
                    if marca == 'dex': return 'DEX'
                    if marca == 'round5': return 'Round5'
                    if marca == 'sevenhero': return 'Sevenhero'
                    if marca == 'hq': return 'HQ'
                    if marca == 'axpro': return 'Axpro'
                    if marca == 'odyssey' or marca == 'sansung' or marca == 'samsung': return 'Samsung'
                    if marca == 'cmteck': return 'CMTECK'
                    if marca == 'ilectry vision': return 'Ilectry Vision'
                    if marca == 'xlinne': return 'Xlinne'
                    if marca == 'worldview': return 'Worldview'
                    if marca == '3geen' or marca == '3green': return '3Green'
                    if marca == 'ntc': return 'NTC'
                    if marca == 'bestbattery': return 'BestBattery'
                    if marca == 'bestoss': return 'Bestoss'
                    if marca == 'synex': return 'Synex'
                    if marca == 'sgmax': return 'SGMAX'
                    if marca == 'fanxiang': return 'Fanxiang'
                    if marca == 'polyvox': return 'Polyvox'
                    if marca == 'vokal': return 'Vokal'
                    if marca == 'kaidi': return 'Kaidi'
                    if marca == 'microdigi': return 'Microdigi'
                    if marca == 'playshop': return 'Playshop'
                    if marca == 'g-fire': return 'G-Fire'
                    if marca == 'nextpc': return 'NextPC'
                    if marca == 'gbt': return 'GBT'
                    if marca == 'pctop': return 'PCTOP'
                    if marca == 'mxt': return 'MXT'
                    if marca == 'kapbom': return 'Kapbom'
                    if marca == 'ebai': return 'Ebai'
                    if marca == 'ckmova': return 'CKMOVA'
                    if marca == 'mirfak': return 'Mirfak'
                    if marca == 'sairen': return 'Sairen'
                    if marca == 'csr': return 'CSR'
                    if marca == 'santo angelo': return 'Santo Angelo'
                    if marca == 'ajazz': return 'Ajazz'
                    if marca == 'cross do brasil': return 'Cross do Brasil'
                    if marca == 'g-hox': return 'G-Hox'
                    if marca == 'byz': return 'BYZ'
                    return marca.strip().capitalize()
                elif marca == 'kbm! gaming' and 'kbm! gaming' in nome_lower:
                    return 'KBM! Gaming' 
            
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
            
            # FILTRO APRIMORADO PARA MOUSES E MOUSEPADS
            buscando_mousepad = 'mousepad' in termo_limpo or 'mouse pad' in termo_limpo
            
            # Só aplica os bloqueios de mouse SE o utilizador NÃO estiver à procura de um mousepad
            if 'mouse' in termo_limpo and not buscando_mousepad:
                # 1. Bloqueia acessórios (porque o utilizador quer um MOUSE de verdade)
                if 'mousepad' in nome_limpo or 'mouse pad' in nome_limpo or 'bungee' in nome_limpo or 'grip tape' in nome_limpo or 'skate' in nome_limpo or 'feet' in nome_limpo:
                    return False
                
                # 2. Bloqueia "Kits", "Combos" e "Teclados" disfarçados de mouse
                if 'teclado' in nome_limpo or 'kit' in nome_limpo or 'combo' in nome_limpo:
                    return False

                # 3. A Regra do "Gamer"
                if 'gamer' not in termo_limpo and 'gamer' in nome_limpo:
                    return False
            
            # FILTRO APRIMORADO PARA HEADSETS
            if 'headset' in termo_limpo:
                # 1. Bloqueia acessórios e peças de reposição (almofadas, suportes, etc.)
                acessorios_headset = ['suporte', 'almofada', 'espuma', 'earpad', 'estojo', 'case', 'arco', 'haste']
                if any(acessorio in nome_limpo for acessorio in acessorios_headset):
                    return False
                
                # 2. Bloqueia Kits (reforço para evitar combos de teclado/mouse/headset)
                if 'kit' in nome_limpo or 'combo' in nome_limpo:
                    return False

                # 3. A Regra do "Gamer"
                # Se o usuário NÃO digitou "gamer" na busca, bloqueia os headsets que são gamer no nome
                if 'gamer' not in termo_limpo and 'gamer' in nome_limpo:
                    return False

            if 'monitor' in termo_limpo or 'tela' in termo_limpo:
                if 'suporte' in nome_limpo or 'braco' in nome_limpo or 'articulado' in nome_limpo or 'pistao' in nome_limpo or 'barra de led' in nome_limpo or 'limpeza' in nome_limpo:
                    return False
            
            # FILTRO APRIMORADO PARA TECLADOS
            if 'teclado' in termo_limpo:
                # 1. Bloqueia acessórios (peças e mods)
                if 'keycap' in nome_limpo or 'switch ' in nome_limpo or 'apoio' in nome_limpo or 'mousepad' in nome_limpo or 'adesivo' in nome_limpo or 'lubrificante' in nome_limpo:
                    return False
                
                # 2. Bloqueia "Kits" e "Combos" (Teclado + Mouse)
                if 'mouse' in nome_limpo or 'kit' in nome_limpo or 'combo' in nome_limpo:
                    return False

                # 3. Separação de Mecânico e Magnético
                buscou_mecanico = 'mecanico' in termo_limpo
                buscou_magnetico = 'magnetico' in termo_limpo

                if buscou_mecanico and not buscou_magnetico:
                    # Se buscou mecânico, bloqueia se tiver "magnetico" no nome do produto
                    if 'magnetico' in nome_limpo:
                        return False
                elif buscou_magnetico and not buscou_mecanico:
                    # Se buscou magnético, a palavra "magnetico" passará a ser obrigatória
                    pass # O filtro final dará conta de exigir a palavra "magnetico"
                
            if 'cabo' in nome_limpo or 'adaptador' in nome_limpo: return False
            
            if 'gabinete' in termo_limpo:
                if 'suporte' in nome_limpo or 'fita' in nome_limpo or 'controladora' in nome_limpo or 'hub' in nome_limpo or 'cabo' in nome_limpo:
                    return False
            
            if 'ssd' in termo_limpo or 'nvme' in termo_limpo or 'm.2' in termo_limpo:
                if 'gaveta' in nome_limpo or 'case' in nome_limpo or 'dissipador' in nome_limpo or 'enclosure' in nome_limpo:
                    return False
            
            # 🚀 CORREÇÃO 4: Filtro Inteligente de HD (Disco) vs HD (Resolução)
            buscando_armazenamento = (re.search(r'\bhd\b', termo_limpo) and 'monitor' not in termo_limpo) or 'ssd' in termo_limpo or 'disco' in termo_limpo
            if buscando_armazenamento:
                if 'monitor ' in nome_limpo or 'tela ' in nome_limpo or 'webcam' in nome_limpo or 'camera' in nome_limpo or 'smart tv' in nome_limpo or 'televisao' in nome_limpo:
                    return False
            
            if 'memoria' in termo_limpo or 'ram' in termo_limpo or 'ddr' in termo_limpo:
                if 'processador' in nome_limpo or 'storage' in nome_limpo or re.search(r'\bnas\b', nome_limpo) or 'servidor' in nome_limpo: 
                    return False
            
            if 'placa-mae' not in termo_limpo and 'placa mae' not in termo_limpo and 'motherboard' not in termo_limpo:
                if 'placa-mae' in nome_limpo or 'placa mae' in nome_limpo or 'motherboard' in nome_limpo or 'mainboard' in nome_limpo: return False
            
            # 🚀 CORREÇÃO 1: Filtro inteligente para famílias de processadores
            familias_processadores = ['ryzen', 'core', 'xeon', 'pentium', 'celeron', 'athlon']
            buscando_familia = any(fam in termo_limpo for fam in familias_processadores)
            
            if 'gabinete' not in termo_limpo and 'cpu' not in termo_limpo and 'processador' not in termo_limpo and not buscando_familia:
                if nome_limpo.startswith('gabinete'): return False
                if nome_limpo.startswith('processador'): return False
            
            if 'cooler' not in termo_limpo and 'water' not in termo_limpo and 'fan' not in termo_limpo:
                if nome_limpo.startswith('cooler ') or nome_limpo.startswith('water ') or nome_limpo.startswith('fan '): return False
                if 'cooler para' in nome_limpo or 'cooler processador' in nome_limpo or 'water cooler' in nome_limpo or 'watercooler' in nome_limpo: return False
                if 'ventoinha' in nome_limpo or 'dissipador' in nome_limpo: return False
            
            # 🚀 CORREÇÃO 5: Liberação da palavra "Tela" se o alvo for um monitor
            if 'notebook' in nome_limpo or 'laptop' in nome_limpo or 'book' in nome_limpo: return False
            if 'monitor' not in termo_limpo and 'tela' not in termo_limpo and 'tela' in nome_limpo: return False
            
            if 'kit' in nome_limpo or 'combo' in nome_limpo or 'upgrade' in nome_limpo: return False
            
            if 'enterprise' in nome_limpo or 'servidor' in nome_limpo or 'server' in nome_limpo: return False
            
            if 'super' not in termo_limpo and re.search(r'\bsuper\b', nome_limpo): return False
            if 'ti' not in termo_limpo and re.search(r'\bti\b', nome_limpo): return False
            if 'xt' not in termo_limpo and re.search(r'\bxt\b', nome_limpo): return False
            if 'xtx' not in termo_limpo and re.search(r'\bxtx\b', nome_limpo): return False
                
            # 🚀 CORREÇÕES 2, 3 e 6: Filtro flexível para Placa-Mãe, Memórias, Gabinetes e Valores Alfanuméricos
            palavras_da_busca = termo_limpo.split()
            
            # Flexibilidade Placa-Mãe
            if "placa" in palavras_da_busca and "mae" in palavras_da_busca:
                palavras_da_busca = [p for p in palavras_da_busca if p not in ["placa", "mae"]]
                
            # Flexibilidade Memória RAM
            if "memoria" in palavras_da_busca and "ram" in palavras_da_busca:
                palavras_da_busca.remove("ram")
                
            # Flexibilidade Gabinete
            if "gabinete" in palavras_da_busca and "gamer" in palavras_da_busca:
                palavras_da_busca.remove("gamer")

            for palavra in palavras_da_busca:
                # Se for número puro
                if palavra.isdigit():
                    if not re.search(rf'(?<!\d){palavra}(?!\d)', nome_limpo):
                        return False
                        
                # Se for alfanumérico (ex: 8gb, 3200mhz, 13600k)
                elif any(char.isdigit() for char in palavra):
                    # 🚀 NOVO: Flexibilidade para processadores com letras (K, F, KF, X, XT, X3D)
                    # Verifica se a palavra está no nome OU se a palavra sem a última letra está no nome
                    # Ex: se palavra for "13600k", aceita se achar "13600k" ou "13600 k" ou apenas "13600" (se for o caso da loja omitir)
                    match = re.match(r'^(\d+)([a-zA-Z]+)$', palavra)
                    if match:
                        num_part = match.group(1)
                        letra_part = match.group(2)
                        
                        # Tenta achar exato (13600k), com espaço (13600 k) ou só o número com limite
                        if palavra in nome_limpo or f"{num_part} {letra_part}" in nome_limpo:
                             pass # Passou
                        else:
                             return False
                    else:
                        if palavra not in nome_limpo:
                            return False
                            
                # Se for palavra normal
                else:
                    if palavra not in nome_limpo:
                        return False
            return True
            
        data_atual = datetime.now().strftime("%Y-%m-%d") 
        
# ================= 1. RASPANDO A KABUM =================
        try:
            url_kabum = f"https://www.kabum.com.br/busca/{termo_busca.replace(' ', '-')}"
            print(f"\n🔍 [DEBUG KBM] Acessando: {url_kabum}")
            navegador.get(url_kabum)
            time.sleep(5) 
            
            for _ in range(5):
                navegador.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1)

            cards = navegador.find_elements(By.XPATH, "//a[contains(@href, '/produto/')]")
            print(f"📦 [DEBUG KBM] Encontrados {len(cards)} cards de produtos.")

            for card in cards:
                try:
                    texto_completo = card.get_attribute('aria-label')
                    if not texto_completo:
                        texto_completo = card.text.replace('\n', ' ')
                        
                    if not texto_completo:
                        continue 

                    nome_separado = re.split(r', avaliação|, R\$', texto_completo)[0].strip()
                    
                    # 🚀 TRAVA DE SEGURANÇA (Anti Falsos Positivos do "Ti")
                    termo_busca_minusculo = termo_busca.lower()
                    nome_minusculo = nome_separado.lower()
                    if " ti" in termo_busca_minusculo and " ti" not in nome_minusculo:
                        continue 
                        
                    if not produto_eh_valido(nome_separado, termo_busca):
                        continue

                    # 🚀 O NOVO EXTRATOR BLINDADO (Imune a espaços e formatações exóticas)
                    valores_encontrados = re.findall(r'R\$\s*([0-9]+(?:[\.,\s]+[0-9]+)*)', texto_completo)
                    
                    precos_validos = []
                    for valor in valores_encontrados:
                        valor_limpo = valor.strip()
                        # Procura o último separador (ponto ou vírgula) para isolar os centavos
                        match = re.search(r'([\.,])(\d{1,2})$', valor_limpo)
                        try:
                            if match:
                                cents = match.group(2)
                                if len(cents) == 1: cents += '0'
                                # Pega tudo antes dos centavos e arranca espaços ou pontos de milhar
                                inteiros = re.sub(r'\D', '', valor_limpo[:match.start()])
                                if inteiros == '': inteiros = '0'
                                precos_validos.append(float(f"{inteiros}.{cents}"))
                            else:
                                inteiros = re.sub(r'\D', '', valor_limpo)
                                if inteiros: precos_validos.append(float(inteiros))
                        except:
                            pass
                    
                    if precos_validos:
                        # Agora sim! Como os números gigantes foram lidos corretamente, ele vai escolher o preço cheio!
                        preco_final = max(precos_validos)
                        
                        marca = extrair_marca(nome_separado)
                        partes_nome = re.split(r',\s*|;\s*|\s+-\s+', nome_separado, maxsplit=1)
                        nome_curto = partes_nome[0].strip()
                        descricao = partes_nome[1].strip() if len(partes_nome) > 1 else ""
                        
                        # 🚀 NOVA BLINDAGEM DE PADRONIZAÇÃO NO BANCO
                        nome_curto = nome_curto.upper()
                        nome_curto = re.sub(r'\s+\|\s+TERABYTE.*|\s+\|\s+KABUM.*', '', nome_curto)
                        nome_curto = re.sub(r'\s+', ' ', nome_curto).strip()
                        
                        lista_produtos.append({
                            "Data": data_atual,
                            "Loja": "Kabum",
                            "Marca": marca,
                            "Produto": nome_curto,
                            "Descrição": descricao,
                            "Preço": preco_final
                        })
                except Exception as inner_e:
                     pass 

        except Exception as e:
            print(f"❌ [DEBUG KBM] Erro fatal ao raspar Kabum: {e}")

        # ================= 2. RASPANDO A TERABYTE =================
        try:
            url_terabyte = f"https://www.terabyteshop.com.br/busca?str={termo_busca.replace(' ', '+')}"
            print(f"\n🔍 [DEBUG TERA] Acessando: {url_terabyte}")
            navegador.get(url_terabyte)
            time.sleep(5) 
            
            for _ in range(10):
                navegador.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1)
            
            # 🚀 AS NOVAS CLASSES ATUALIZADAS AQUI:
            nomes_tera = navegador.find_elements(By.CSS_SELECTOR, '.tss-card-name')
            precos_tera = navegador.find_elements(By.CSS_SELECTOR, '.tss-card-price')
            
            print(f"📦 [DEBUG TERA] Encontrados {len(nomes_tera)} nomes e {len(precos_tera)} preços.")
            
            for nome_el, preco_el in zip(nomes_tera, precos_tera):
                nome_completo = nome_el.get_attribute('textContent').strip()
                if not produto_eh_valido(nome_completo, termo_busca): continue
                    
                preco_texto = preco_el.get_attribute('textContent')
                numeros_e_virgula = re.sub(r'[^\d,]', '', preco_texto)
                
                if numeros_e_virgula:
                    preco_limpo = numeros_e_virgula.replace(',', '.')
                    marca = extrair_marca(nome_completo)
                    
                    partes_nome = re.split(r',\s*|;\s*|\s+-\s+', nome_completo, maxsplit=1)
                    nome_curto = partes_nome[0].strip()
                    descricao = partes_nome[1].strip() if len(partes_nome) > 1 else ""
                    
                    # 🚀 NOVA BLINDAGEM DE PADRONIZAÇÃO NO BANCO
                    nome_curto = nome_curto.upper()
                    nome_curto = re.sub(r'\s+\|\s+TERABYTE.*|\s+\|\s+KABUM.*', '', nome_curto)
                    nome_curto = re.sub(r'\s+', ' ', nome_curto).strip()
                    
                    try: 
                        lista_produtos.append({
                            "Data": data_atual, 
                            "Loja": "Terabyte",
                            "Marca": marca,
                            "Produto": nome_curto,          
                            "Descrição": descricao,         
                            "Preço": float(preco_limpo)
                        })
                    except: pass
        except Exception as e:
            print(f"❌ [DEBUG TERA] Erro ao raspar Terabyte: {e}")

        navegador.quit()
        
        if len(lista_produtos) > 0:
            df_resultados = pd.DataFrame(lista_produtos)
            
            df_resultados = df_resultados.drop_duplicates(subset=['Loja', 'Produto', 'Descrição'], keep='first')
            df_resultados = df_resultados.sort_values(by="Preço", ascending=True).reset_index(drop=True)
# ================= 2. RASPANDO A TERABYTE =================
        try:
            url_terabyte = f"https://www.terabyteshop.com.br/busca?str={termo_busca.replace(' ', '+')}"
            print(f"\n🔍 [DEBUG TERA] Acessando: {url_terabyte}")
            navegador.get(url_terabyte)
            time.sleep(5) 
            
            for _ in range(10):
                navegador.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1)
            
            # 🚀 AS NOVAS CLASSES ATUALIZADAS AQUI:
            nomes_tera = navegador.find_elements(By.CSS_SELECTOR, '.tss-card-name')
            precos_tera = navegador.find_elements(By.CSS_SELECTOR, '.tss-card-price')
            
            print(f"📦 [DEBUG TERA] Encontrados {len(nomes_tera)} nomes e {len(precos_tera)} preços.")
            
            for nome_el, preco_el in zip(nomes_tera, precos_tera):
                nome_completo = nome_el.get_attribute('textContent').strip()
                if not produto_eh_valido(nome_completo, termo_busca): continue
                    
                preco_texto = preco_el.get_attribute('textContent')
                numeros_e_virgula = re.sub(r'[^\d,]', '', preco_texto)
                
                if numeros_e_virgula:
                    preco_limpo = numeros_e_virgula.replace(',', '.')
                    marca = extrair_marca(nome_completo)
                    
                    partes_nome = re.split(r',\s*|;\s*|\s+-\s+', nome_completo, maxsplit=1)
                    nome_curto = partes_nome[0].strip()
                    descricao = partes_nome[1].strip() if len(partes_nome) > 1 else ""
                    
                    try: 
                        lista_produtos.append({
                            "Data": data_atual, 
                            "Loja": "Terabyte",
                            "Marca": marca,
                            "Produto": nome_curto,          
                            "Descrição": descricao,         
                            "Preço": float(preco_limpo)
                        })
                    except: pass
        except Exception as e:
            print(f"❌ [DEBUG TERA] Erro ao raspar Terabyte: {e}")

        navegador.quit()
        
        if len(lista_produtos) > 0:
            df_resultados = pd.DataFrame(lista_produtos)
            
            df_resultados = df_resultados.drop_duplicates(subset=['Loja', 'Produto', 'Descrição'], keep='first')
            df_resultados = df_resultados.sort_values(by="Preço", ascending=True).reset_index(drop=True)
            
            # ========================================================
            # 🚨 INTEGRAÇÃO AWS: MOTOR DE INJEÇÃO SQL SERVER
            # ========================================================
            if salvar_no_banco:
                try:
                    from sqlalchemy import create_engine
                    import urllib.parse
                    
                    print("☁️ Conectando ao banco de dados na AWS para salvar...")
                    
                    # Credenciais validadas
                    endpoint_aws = "hardwares-tcc.cveowcsuansb.sa-east-1.rds.amazonaws.com"
                    senha_aws = "milanhaverso2" 
                    usuario_aws = "lcpctcc"
                    
                    # Formato seguro
                    senha_codificada = urllib.parse.quote_plus(senha_aws)
                    url_conexao = f"mssql+pyodbc://{usuario_aws}:{senha_codificada}@{endpoint_aws}/tcc_hardware?driver=ODBC+Driver+17+for+SQL+Server"
                    engine = create_engine(url_conexao)
                    
                    # Injeta no banco e cria a tabela 'HistoricoPrecos' se ela não existir
                    df_aws = df_resultados.rename(columns={
                        'Data': 'DataCaptura',
                        'Preço': 'Preco',
                        'Descrição': 'Descricao'
                    })
                    
                    df_aws.to_sql('HistoricoPrecos', con=engine, if_exists='append', index=False)
                    print("✅ Sucesso: Tabela criada e atualizada na AWS!")
                    
                except Exception as aws_erro:
                    print(f"❌ Erro ao tentar salvar na AWS: {aws_erro}")
            # ========================================================
            
            qtd_kabum = len(df_resultados[df_resultados['Loja'] == 'Kabum'])
            qtd_terabyte = len(df_resultados[df_resultados['Loja'] == 'Terabyte'])
            
            # Formata a coluna Preço para o output na tela ficar bonito
            df_tela = df_resultados.rename(columns={'Preço': 'Preço (R$)'})
            
            return {
                "total_encontrados": len(df_tela), 
                "total_kabum": qtd_kabum,       
                "total_terabyte": qtd_terabyte, 
                "preco_minimo": df_tela["Preço (R$)"].min(), 
                "preco_medio": df_tela["Preço (R$)"].mean(),
                "dados_completos": df_tela, 
            }
        return None
    except Exception as e:
        print(f"Erro crítico no WebDriver: {e}")
        traceback.print_exc()
        return None