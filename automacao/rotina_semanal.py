import time
from datetime import datetime
from bot_scraping import escanear_mercado_completo
import requests
import pandas as pd

try:
    from conexao_aws import criar_engine_aws
except ImportError:
    from automacao.conexao_aws import criar_engine_aws

pecas_para_monitorar = [

    # 🎮 PLACAS DE VÍDEO - NVIDIA (Mais completa)
    "gt610",
    "gt730",
    "gt740",
    "gtx 750 ti",
    "gtx960",
    "gtx1050 ti",
    "gtx 1650",
    "gtx 1650ti",
    "gtx 1660",
    "gtx 1660 ti",
    "gtx 1660 super",
    "rtx 2060",
    "rtx 2080",
    "rtx 2080 super",
    "rtx 3050",
    "rtx 3060",
    "rtx 4060",
    "rtx 4060 ti",
    "rtx 5050",
    "rtx 5060",
    "rtx 5060 ti",
    "rtx 5070",
    "rtx 5070 ti",
    "rtx 5080",
    "rtx 5090",

    # 🎮 PLACAS DE VÍDEO - AMD
    "rx 560",
    "rx 550",
    "rx 570",
    "rx 580",
    "rx 590",
    "rx 6400",
    "rx 6500 xt",
    "rx 6600",
    "rx 6750 xt",
    "rx 7600",
    "rx 7600 xt",
    "rx 7700 xt",
    "rx 9070",
    "rx 9070 xt",
    "rx 9060 xt",
    "rx 9060",
    "rx 9070",
    "rx 9070 gre",

    # 🔵 PLACAS DE VÍDEO - INTEL
    "arc a580",
    "arc a380",
    "arc a750",
    "arc a770",
    "arc b570",
    "arc b580",

    # 🧠 PROCESSADORES (A "SALA DOS PROFESSORES" DA AMD)

    # --- Série 4000 (APUs e Entrada) ---
    "ryzen 3 4100", "ryzen 5 4500",
    # --- Série 5000 (O grande volume do mercado) ---
    "ryzen 5 5600", "ryzen 5 5600x", "ryzen 5 5600g","ryzen 5 5600gt",
    "ryzen 7 5700", "ryzen 7 5700x", "ryzen 7 5700g",
    "ryzen 7 5800", "ryzen 7 5800x",
    "ryzen 9 5900x",
    
    # --- Série 7000 (Zen 4 Principais e X3D) ---
    "ryzen 5 7600", "ryzen 5 7600x", 
    "ryzen 7 7700x", "ryzen 7 7800x3d", 
    "ryzen 9 7900", "ryzen 9 7900x",
    "ryzen 9 7950x",
    
    # --- Série 8000 (APUs Zen 4) ---
    "ryzen 5 8500g", "ryzen 5 8600g", "ryzen 7 8700g",
    
    # --- Série 9000 (Nova Geração Zen 5) ---
    "ryzen 5 9600x", 
    "ryzen 7 9700x", 
    "ryzen 9 9900x", "ryzen 9 9950x",
    "ryzen 9 9950x3d","ryzen 9 9900x3d",
   
    # 🧠 PROCESSADORES INTEL (A "Sala dos Professores" Azul)
    
    # --- 12ª Geração (Alder Lake - Custo-Benefício de Entrada) ---
    "core i3 12100f", "core i5 12400f", "core i5 12600k", 
    "core i7 12700k", "core i9 12900k",
    
    # --- 13ª Geração (Raptor Lake - Alto Volume de Vendas) ---
    "core i3 13100f", "core i5 13400f","core i7 13700k",
    
    # --- 14ª Geração (Raptor Lake Refresh - Alta Performance) ---
    "core i3 14100f", "core i5 14400f", "core i5 14600k", "core i5 14600kf",
    "core i7 14700k", "core i7 14700kf", "core i9 14900k",
    # --- Core Ultra (Nova Nomenclatura / Última Geração) ---
    "core ultra 5 245k", "core ultra 5 245kf", 
    "core ultra 7 265k", "core ultra 7 265kf", 
    "core ultra 9 285k",

  
    # 🏗️ PLACAS-MÃE (Fundação do Hardware)
    
    # --- AMD AM4 (Para Ryzen 3000, 4000 e 5000) ---
    "placa mae a320m", "placa mae a520m", 
    "placa mae b450m", "placa mae b550m", 
    "placa mae b550", "placa mae b450",
    
    # --- AMD AM5 (Para Ryzen 7000, 8000 e 9000) ---
    "placa mae a620m", "placa mae b650m", 
    "placa mae b650", "placa mae b650e",
    "placa mae x670",
    "placa mae x870", "placa mae x870e",
    
    # --- Intel LGA 1700 (Para 12ª, 13ª e 14ª Geração) ---
    "placa mae h610m", "placa mae b660m", 
    "placa mae b760m", "placa mae b760",
    "placa mae z690", "placa mae z790",
    
    # --- Intel LGA 1851 (Para Core Ultra Série 200S) ---
    "placa mae z890", "placa mae z890m",

    # ⚡ MEMÓRIA RAM
    "memoria ddr4 8gb",
    "memoria ddr4 16gb",
    "memoria ddr4 32gb",
    "memoria ddr5 16gb",
    "memoria ddr5 32gb",
    "memoria ddr5 64gb",

    # 💾 ARMAZENAMENTO
    "ssd 480gb",
    "ssd 1tb",
    "ssd 500gb",
    "ssd 2tb",
    "ssd 4tb",
    "hd 1tb",
    "hd 2tb",
    "hd 4tb",

    # 🖥️ MONITORES
    "monitor 75hz",
    "monitor 100hz",
    "monitor 144hz",
    "monitor 165hz",
    "monitor 240hz",
    "monitor 280hz",
    "monitor 360hz",
    "monitor 4k",
    "monitor 2k",
    "monitor ultrawide",

    # 🌬️ REFRIGERAÇÃO
    "air cooler cpu",
    "water cooler 120mm",
    "water cooler 240mm",
    "water cooler 360mm",
    "fan rgb",
    "fan 120mm",
    "fan 140mm",

    # 🖥️ GABINETES
    "gabinete aquario",
    "gabinete mid tower",
    "gabinete full tower",
    "gabinete mini itx",

    # 🔌 FONTES
    "fonte 500w",
    "fonte 600w",
    "fonte 650w",
    "fonte 750w",
    "fonte 850w",
    "fonte 1000w",
    "fonte 1200w",

    # 🎮 PERIFÉRICOS/COMPLEMENTOS
    "mouse gamer",
    "mouse",
    "teclado mecanico",
    "teclado magnético",
    "headset gamer",
    "headset",
    "mousepad gamer",
    "webcam",
    "soundbar",
    "microfone",
]
def registrar_dolar_do_dia():
    print("\n==================================================")
    print("💵 INICIANDO CAPTURA DO DÓLAR (API BANCÁRIA)")
    print("==================================================")
    try:
        # 1. Bate na porta da API pública de moedas
        resposta = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL", timeout=15)
        resposta.raise_for_status()
        dados = resposta.json()
        
        # 2. Extrai o valor de compra (bid)
        valor_dolar = float(dados['USDBRL']['bid'])
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        
        print(f"💰 Dólar Hoje ({data_hoje}): R$ {valor_dolar:.2f}")
        
        # 3. Prepara a mini-tabela do Pandas
        df_dolar = pd.DataFrame({
            "DataCaptura": [data_hoje],
            "ValorDolar": [valor_dolar]
        })
        
        print("Conectando à AWS para salvar o dólar...")
        engine = criar_engine_aws(timeout=20)
        
        # if_exists='append' vai criar a tabela HistoricoDolar na AWS se ela não existir!
        with engine.begin() as conexao:
            df_dolar.to_sql('HistoricoDolar', con=conexao, if_exists='append', index=False)
        print("✅ Dólar salvo na nuvem AWS com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao capturar/salvar o dólar: {e}")

# CHAMA A FUNÇÃO DO DÓLAR ANTES DE COMEÇAR O SCRAPING

registrar_dolar_do_dia()

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 INICIANDO ROTINA DE EXTRAÇÃO SEMANAL...")
print(f"Total de itens a pesquisar: {len(pecas_para_monitorar)}")

# 2. O Loop de Extração
for i, peca in enumerate(pecas_para_monitorar, 1):
    print(f"\n[{i}/{len(pecas_para_monitorar)}] Pesquisando: {peca}")
    
    # Chama o bot e LIGA a chave para salvar na AWS
    escanear_mercado_completo(peca, salvar_no_banco=True)
    
    # Pausa de 15 segundos entre cada pesquisa para não bloquear o seu IP nas lojas!
    if i < len(pecas_para_monitorar):
        print("⏳ Pausando 10 segundos para evitar bloqueios de segurança...")
        time.sleep(10)

print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ ROTINA FINALIZADA COM SUCESSO!")
