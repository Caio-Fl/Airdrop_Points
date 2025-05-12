import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import time
from datetime import datetime, timezone
from get_leader_OpenEden_function import get_leader_OpenEden_function
from get_leader_Level_function import get_leader_Level_function
from get_fragmetric_data import get_fragmetric_data
from get_Pendle_Data import get_Pendle_Data
from get_rateX_data import get_rateX_data
from get_leader_kyros_function import get_leader_kyros_function
from get_defillama_info import get_defillama_info
from protocol_rate import protocol_rate
from getAllPendleMarkets import get_pendle_apy_data, get_pendle_markets
from PIL import Image
import webbrowser
import sqlite3
import json
from streamlit_option_menu import option_menu

# --- Configurações da Página ---
#st.set_page_config(page_title="Pendle Airdrop Farm", layout="wide")

# Configuração da página (sempre primeiro!)
st.set_page_config(
    page_title="Fleming Airdrop Monitor",
    page_icon="🪂",
    layout="wide"
)

# Adicionando CSS para os botões de navegação
st.markdown("""
    <style>
        .stButton > button {
            background-color: #342b44;  /* Cor do botão */
            color: white;  /* Cor do texto */
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #45a049;  /* Cor do botão ao passar o mouse */
            color: #342b44;  /* Cor do texto */
        }
    </style>
""", unsafe_allow_html=True)

# --- Estilização Customizada ---
st.markdown("""
    <style>
        .header {
            background-color: #342b44;
            border-radius: 8px;
            border: 2px solid #FFFFFF; 
            padding: 10px;
            text-align: center;
            color: white;
            font-size: 40px;
            font-weight: bold;
        }
        .footer {
            background-color: #342b44;
            border-radius: 8px;
            border: 2px solid #FFFFFF; 
            color: white;
            text-align: center;
            padding: 1rem;
            font-size: 14px;
        }
        .card {
            border: 2px solid black;
            padding: 1rem;
            text-align: center;
            border-radius: 10px;
            background-color: #f9f9f9;
            margin-bottom: 2rem;
            cursor: pointer;
        }
    </style>
""", unsafe_allow_html=True)

# Letreiro de divulgação de informações
st.markdown("""
<style>
.marquee-container {
  width: 100%;
  overflow: hidden;
  background-color: #FFA500;
  border-radius: 8px;
  border: 2px solid #FFFFFF; 
  color: white;
  font-size: 26px;
  padding: 10px;
  box-sizing: border-box;
  position: relative;
  height: 70px;
            
  /* Centralização do conteúdo */
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.marquee-text {
  display: inline-block;
  white-space: nowrap;
  position: absolute;
  will-change: transform;
  animation: marquee 30s ease-in-out infinite;
}
            

@keyframes marquee {
  0%   { transform: translateX(160%); }
  25%  { transform: translateX(0%); }     /* Chega ao centro */
  75%  { transform: translateX(0%); }     /* Fica parado no centro */
  100% { transform: translateX(-160%); }  /* Sai pela esquerda */
}
</style>

<div class="marquee-container">
  <div class="marquee-text">
    🚨 Last News: <a href='https://claim.resolv.xyz/' target='_blank' style='color:#342b44;'>Register to Receive Airdrop from Resolv Protocol (Up to 16/05/2025)!</a> / <a href='https://dood.doodles.app/' target='_blank' style='color:#342b44;'>Claim do Airdrop DOODLES Available!</a>
  </div>
</div>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header"> Airdrops Monitor </div>', unsafe_allow_html=True)

st.markdown(
    "<hr style='border: 2px double #342b44;'>",
    unsafe_allow_html=True
)
# --- Sidebar ---
st.sidebar.title("Airdrops Monitor")
st.sidebar.markdown("---")
st.sidebar.title("Menu")
st.sidebar.markdown("<h3 style='font-size: 20px;'></h3>", unsafe_allow_html=True)

# Define options for the sidebar

options = ["Welcome","Farm with YT", "Comparative YT Table", "Pendle APY Prediction",
            "Latest Airdrops", "Depin Airdrops", "Bridges & Swaps Protocols", "Revoke Contract"]
    
opcao = st.sidebar.selectbox("", options)
st.markdown("\n\n")
st.sidebar.markdown("---")


# --- Inicializar o banco de dados ---
def init_db():
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS json_data (
            id INTEGER PRIMARY KEY,
            dados_json TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Deletar json no BD
def deletar_json():
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM json_data WHERE id = 1')
    conn.commit()
    conn.close()

# --- Salvar JSON no banco (mantém só o último) ---
def salvar_json(dado_dict):
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    json_str = json.dumps(dado_dict)
    cursor.execute('''
        INSERT INTO json_data (id, dados_json) VALUES (1, ?)
        ON CONFLICT(id) DO UPDATE SET dados_json=excluded.dados_json;
    ''', (json_str,))
    conn.commit()
    conn.close()

# --- Carregar único registro ---
def carregar_json():
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    cursor.execute('SELECT dados_json FROM json_data WHERE id = 1')
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return {}

# --- Inicializa DB ---
init_db()
#deletar_json()
# Faz a busca de dados da OpenEden e Level em suas API's
def enviar_dados():
    try:
        Total_OpenEden,top100p_OpenEden,Open_count = get_leader_OpenEden_function()
        time_Open = datetime.now().now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        Total_Level,top100p_Level,Level_count = get_leader_Level_function()
        time_Level = datetime.now().now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        tags = ["OpenEden","Level"]
        values = [Total_OpenEden,Total_Level]
        top100 = [top100p_OpenEden,top100p_Level]
        total_users = [Open_count,Level_count]
        dado = {
            "tag": tags[0],
            "value": values[0]
        }
    except:
        st.warning("⚠️ Não foi possível conectar à API.")
    return(tags,values,time_Open,time_Level,top100,total_users)


# Inicialização de parâmetros de cada protocolo

i = 0
# OpenEden
Open_Data = []
Open_Multipleir = 10
Open_Boost = 1.05
Open_TP_0 = 9851534492
Open_pts_token = 1
Open_date0 = datetime.strptime("2025-04-09T08:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

# Level
Level_Data = []
Level_Multipleir = 40
Level_Boost = 1.10
Level_TP_0 = 117375084663151
Level_pts_token = 2400
Level_date0 = datetime.strptime("2025-03-27T08:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

# Fragmetric
Frag_Data = []
Frag_Multipleir = 4
Frag_Boost = 1.10
Backpack_Boost = 1.30
Frag_TP_0 = 9710000000
Frag_pts_token = 86.4
Frag_date0 = datetime.strptime("2025-04-07T08:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

# Kyros
Ky_Data = []
Ky_Multipleir = 4
Ky_Boost = 1.10
Ky_TP_0 = 881892008
ky_pts_token = 1
Ky_date0 = datetime.strptime("2025-04-18T08:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

# --- Dados dos Protocolos ---
# Armazena a hora da primeira execução na sessão do usuário
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()
    st.session_state.first_run = True  # flag de primeira execução
else:
    st.session_state.first_run = False

# Hora atual
now = datetime.now()

# Calcula a diferença em segundos
elapsed_seconds = (now - st.session_state.start_time).total_seconds()

# Carrega dados do BD
try:
    protocolos = carregar_json()
    print(protocolos)
except:
    protocolos = {}
    print("No data in DB")

# Aplica CSS customizado para mudar o tamanho da fonte da sidebar
st.markdown("""
    <style>
    /* Altera a fonte de toda a sidebar */
    section[data-testid="stSidebar"] * {
        font-size: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Conteúdo Principal ---
st.title(opcao)

if opcao == "Welcome":
        
    st.markdown(
        """
        <style>
        .airdrop-description {
            font-size: 24px;
            line-height: 1.6;
            text-align: justify;
        }
        </style>
        
        <div class="airdrop-description">
        
        ## Welcome to Airdrops Monitor
        
        The goal of this site is to provide a platform dedicated to airdrop enthusiasts in the world of cryptocurrencies, offering a practical and efficient way to stay updated on the latest news and opportunities that arise. 
        If you are passionate about crypto assets and want to stay ahead in the world of airdrops, this site is your ally to ensure you don’t miss any valuable opportunities in the market.""",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
        .airdrop-description {
            font-size: 22px;
            line-height: 1.6;
            font-weight: bold; 
        }
        </style>
        
        <div class="airdrop-description">
        What Are Airdrops and How Can You Benefit from Them?
        
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
        .airdrop-description {
            font-size: 22px;
            line-height: 1.6;
        }
        </style>
        
        <div class="airdrop-description">

        There are two main types of airdrops:

        - **Task-based airdrops**: Also known as *bounties*, these require you to complete easy tasks like following a Twitter account, sharing a post, or joining a Telegram group. In return, you receive tokens from the project.

        - **Holder airdrops**: Some projects reward users simply for holding certain cryptocurrencies in their wallets. If you qualify, the tokens are automatically sent to you — no need to register or interact.

        Participating in airdrops is an accessible and educational way to get involved in the crypto space, especially for beginners. Best of all, you can grow your portfolio with real value without investing money upfront.

        Browse our list of active airdrops, track new opportunities in real time, and start earning free crypto today!
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
        .airdrop-description {
            font-size: 22px;
            line-height: 1.6;
            font-weight: bold; 
        }
        </style>
        
        <div class="airdrop-description">
        About Me...
        
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
        .airdrop-description {
            font-size: 22px;
            line-height: 1.6;
            text-align: justify;
        }
        </style>
        
        <div class="airdrop-description">

        I am a graduate in electrical-electronic engineering and a PhD in signal processing, with a deep passion for the world of investments. Throughout my career, I have had the opportunity to combine my technical knowledge with my curiosity about the financial universe, especially in the cryptocurrency and airdrop sectors. Over time, I have applied the lessons I learned in engineering to explore new investment opportunities. Additionally, I am a programming enthusiast, with an emphasis on Python, which was the language chosen for the development of this site. My goal is to use both my technical skills and financial experience to provide relevant content and efficient solutions for others who share the same interest in the world of crypto and investments.
        

        </div>
        """,
        unsafe_allow_html=True
    )


elif opcao == "Farm with YT":
    # CSS personalizado para ajustar o tamanho da fonte da sidebar
    st.markdown(
        """
        <style>
        .yt-farm-description {
            font-size: 22px;
            text-align: justify;
            line-height: 1.6;
        }
        </style>

        <div class="yt-farm-description">
            <p>
            Below are the potential returns you can achieve by participating in Yield Token (YT) farming strategies from various protocols that currently have ongoing airdrop campaigns.
            </p>
            <p>
            Each protocol also receives a score based on its potential to deliver solid results, according to the parameters set by the user in the sidebar.
            </p>
            <p>
            To view the full list of parameters for each protocol, double-click on <strong>"View Details"</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Novo Quadro de Inputs ---
    st.sidebar.markdown("<h3 style='font-size: 20px;'>Parameters to YT ROI Estimation</h3>", unsafe_allow_html=True)
    with st.sidebar.expander("", expanded=True):
        invested = st.number_input("Choose the Value to Invest: $", min_value=0.0, value=1000.0, step=1.0)
        tsp = st.number_input("Expected Token Total Supply:", min_value=0, value=1000000000)
        drop = st.number_input("Expected Percentual to Protocol Airdrop:", min_value=0.0, max_value=100.0, value=5.0)
        fdv = st.number_input("Expected FDV in TGE: $", min_value=0.0, value=200000000.0)

        st.markdown("---")
        Level_l_date = st.text_input(
            "Expected Level TGE Date:",
            value="2025-08-08",   # valor padrão
        )
        Open_l_date = st.text_input(
            "Expected OpenEden TGE Date:",
            value="2025-09-30",   # valor padrão
        )
        Frag_l_date = st.text_input(
            "Expected Fragmetric TGE Date:",
            value="2025-09-30",   # valor padrão
        )
        Ky_l_date = st.text_input(
            "Expected Kyros TGE Date:",
            value="2025-07-30",   # valor padrão
        )

    # Verifica se já se passaram 120 segundos
    if elapsed_seconds > 300 or not protocolos:
        with st.spinner('Loading Data and Calculating Parameters...'):
            #try: 
            # Busca Informações no Defillama
            Open_tvl,Open_amount,Open_leadInvestors,Open_otherInvestors = get_defillama_info("openeden","Ethereum")
            Level_tvl,Level_amount,Level_leadInvestors,Level_otherInvestors = get_defillama_info("level","Ethereum")
            Frag_tvl,Frag_amount,Frag_leadInvestors,Frag_otherInvestors = get_defillama_info("fragmetric","Solana")
            Ky_tvl,Ky_amount,Ky_leadInvestors,Ky_otherInvestors = get_defillama_info("kyros","Solana")
            
            # Busca dados dos protocolos em suas respectivas API's
            tags, values, time_Open, time_Level,top100,total_users = enviar_dados()
            Frag_accured,Frag_unApy,solAsUSD,fragAsUSD,fragBySol,Frag_total_users = get_fragmetric_data()
            Ky_accured,Ky_unApy,KyAsUSD,Ky_total_users,Ky_top100p = get_leader_kyros_function()
            
            # Busca dados dos protocolos nas API's da Pendle (Rede Ethereum) e Rate-X (Rede Solana)
            Open_ytMul,Open_unApy,Open_impApy,Open_feeRate,Open_swapFee,Open_ytRoi,Open_expiry,Open_priceImpact = get_Pendle_Data("0xa77c0de4d26b7c97d1d42abd6733201206122e25","0x42E2BA2bAb73650442F0624297190fAb219BB5d5")
            Level_ytMul,Level_unApy,Level_impApy,Level_feeRate,Level_swapFee,Level_ytRoi,Level_expiry,Level_priceImpact = get_Pendle_Data("0xe45d2ce15abba3c67b9ff1e7a69225c855d3da82","0x65901Ac9EFA7CdAf1Bdb4dbce4c53B151ae8d014")
            Frag_ytMul,Frag_Multiplier,Frag_expiry,Frag_swapFee,Frag_priceImpact,time_Frag,symbol_frag = get_rateX_data("fragmetric")
            ky_ytMul,ky_Multiplier,ky_expiry,ky_swapFee,ky_priceImpact,time_ky,symbol_ky = get_rateX_data("kyros")
            print(Level_ytMul)
            # Formata a data atual e as datas de TGE (informadas pelo usuário) para que possam ser subtraídas
            date_obj = datetime.strptime(time_Open, "%Y-%m-%d %H:%M:%S")
            date_utc_formatada = date_obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            date1 = datetime.strptime(date_utc_formatada , "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            date2 = datetime.strptime(Open_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            date3 = datetime.strptime(Level_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            date4 = datetime.strptime(Frag_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            date5 = datetime.strptime(ky_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            print(date5)
            # Calcula os parâmetros de cada Protocolo
            # OpenEden
            Open_date_tge = datetime.strptime((Open_l_date+"T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            Open_mean_daily = 1.3*(values[0]-Open_TP_0)/((date1-Open_date0).days)
            Open_points_tge = round(values[0] + (((Open_date_tge-date1).days)*Open_mean_daily),0)
            Open_points_per_token = round(Open_points_tge/(tsp*drop/100),2)
            Open_farmed_yield = round(invested*Open_ytMul*Open_unApy*(date2-date1).days/365,2)
            Open_daily_pts_farmed = round(invested*Open_ytMul*Open_Multipleir*Open_Boost*Open_pts_token,2)
            Open_total_pts_farmed = round(Open_daily_pts_farmed*(date2-date1).days,2)
            Open_etimated_tokens = round(Open_total_pts_farmed/Open_points_per_token,2)
            Open_airdrop_value = round((fdv/tsp)*Open_etimated_tokens,2)
            Open_cost = abs(round((Open_farmed_yield - invested - (invested*Open_priceImpact)),2))
            Open_profit = round((Open_airdrop_value - Open_cost),2)
            Open_ROI = round((100*Open_profit/Open_cost),2)
            
            Open_grade = protocol_rate(Open_tvl,(100*top100[0]),Open_ROI,(100*Open_mean_daily/values[0]),total_users[0],"excelente")
            
            # Level
            Level_date_tge = datetime.strptime((Level_l_date+"T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            Level_mean_daily = 1.3*(values[1]-Level_TP_0)/((date1-Level_date0).days)
            Level_points_tge = round(values[1] + (((Level_date_tge-date1).days)*Level_mean_daily),0)
            Level_points_per_token = round(Level_points_tge/(tsp*drop/100),2)
            Level_farmed_yield = round(invested*Level_ytMul*Level_unApy*(date3-date1).days/365,2)
            Level_daily_pts_farmed = round(invested*Level_ytMul*Level_Multipleir*Level_Boost*Level_pts_token,2)
            Level_total_pts_farmed = round(Level_daily_pts_farmed*(date3-date1).days,2)
            Level_etimated_tokens = round(Level_total_pts_farmed/Level_points_per_token,2)
            Level_airdrop_value = round((fdv/tsp)*Level_etimated_tokens,2)
            Level_cost = abs(round((Level_farmed_yield - invested - (invested*Level_priceImpact)),2))
            Level_profit = round((Level_airdrop_value - Level_cost),2)
            Level_ROI = round((100*Level_profit/Level_cost),2)

            Level_grade = protocol_rate(Level_tvl,(100*top100[1]),Level_ROI,(100*Level_mean_daily/values[1]),total_users[1],"excelente")

            # Fragmetric
            Frag_date_tge = datetime.strptime((Frag_l_date+"T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            Frag_mean_daily = 1.3*(Frag_accured-Frag_TP_0)/((date1-Frag_date0).days)
            Frag_points_tge = round(Frag_accured + (((Frag_date_tge-date1).days)*Frag_mean_daily),0)
            Frag_points_per_token = round(Frag_points_tge/(tsp*drop/100),2)
            Frag_farmed_yield = round((invested/fragAsUSD)*Frag_ytMul*Frag_unApy*(date4-date1).days/365,2)
            Frag_daily_pts_farmed = round((invested/fragAsUSD)*Frag_ytMul*Frag_Multipleir*Frag_Boost*Backpack_Boost*Frag_pts_token,2)
            Frag_total_pts_farmed = round(Frag_daily_pts_farmed*(date4-date1).days,2)
            Frag_etimated_tokens = round(Frag_total_pts_farmed/Frag_points_per_token,2)
            Frag_airdrop_value = round((fdv/tsp)*Frag_etimated_tokens,2)
            Frag_cost = abs(round(((fragAsUSD*Frag_farmed_yield) - invested - (fragAsUSD*Frag_swapFee)),2))
            Frag_profit = round((Frag_airdrop_value - Frag_cost),2)
            Frag_ROI = round((100*Frag_profit/Frag_cost),2)

            Frag_grade = protocol_rate(Frag_tvl,60,Frag_ROI,(100*Frag_mean_daily/Frag_accured),Frag_total_users,"excelente")

            # Kyros
            Ky_date_tge = datetime.strptime((Ky_l_date+"T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            Ky_mean_daily = 1.3*(Ky_accured-Ky_TP_0)/((date1-Ky_date0).days)
            Ky_points_tge = round(Ky_accured + (((Ky_date_tge-date1).days)*Ky_mean_daily),0)
            Ky_points_per_token = round(Ky_points_tge/((tsp)*2*drop/100),2)
            Ky_farmed_yield = round((invested/KyAsUSD)*ky_ytMul*Ky_unApy*(date5-date1).days/365,2)
            Ky_daily_pts_farmed = round((invested/KyAsUSD)*ky_ytMul*Ky_Multipleir*Ky_Boost*ky_pts_token,2)
            Ky_total_pts_farmed = round(Ky_daily_pts_farmed*(date5-date1).days,2)
            Ky_etimated_tokens = round(Ky_total_pts_farmed/Ky_points_per_token,2)
            Ky_airdrop_value = round((fdv/tsp)*Ky_etimated_tokens,2)
            Ky_cost = abs(round(((KyAsUSD*Ky_farmed_yield) - invested - (KyAsUSD*ky_swapFee)),2))
            Ky_profit = round((Ky_airdrop_value - Ky_cost),2)
            Ky_ROI = round((100*Ky_profit/Ky_cost),2)

            Ky_grade = protocol_rate(Ky_tvl,(100*Ky_top100p),Ky_ROI,(100*Ky_mean_daily/Ky_accured),Ky_total_users,"bom")
            #except:
            #    print("Error in YT Data Request")

        protocolos = {
            "Level": {
                "Imagem": r"C:\Users\0335372\Documents\app_streamlit\Level.jpg",
                "Logo": "https://pbs.twimg.com/profile_images/1811061996172840960/wy0N3CoS_400x400.jpg",
                "Link": "<a href='https://app.level.money/farm?referralCode=pwlblh' target='_blank' style='color:#FFA500;'>More info</a>",
                "Grade": f"{Level_grade}",
                "TVL": f"{Level_tvl} M",
                "Last Update": f"{time_Level}",
                "Expiry": f"{date3.date()}",
                "Total Points Farmed": f"{round(values[1],0)}",
                "YT Multiplier": f"{round(Level_ytMul,3)}",
                "YT APY": f"{round(Level_unApy*100,2)}",
                "Time Until Expiration": f"{(date3-date1)}",
                "Protocol YT Multiplier": f"{Level_Multipleir}",
                "Protocol Referral Boost": f"{round((Level_Boost-1),2)*100} %",
                "Equivalent YT Received": f"$ {round(invested*Level_ytMul,2)}",
                "Daily Points Farmed": f"{Level_daily_pts_farmed}",
                "Total Points Farmed in YT": f"{Level_total_pts_farmed}",
                "Top 100 Concentration": f"{round(100*top100[1],2)}",
                "Total User": f"{total_users[1]}",
                "Farmed Yield in YT": f"$ {Level_farmed_yield}",
                "Mean Daily Points (x 1.30)": f"{round(Level_mean_daily,0)}",
                "Estimated Points in TGE": f"{round(Level_points_tge,0)}",
                "Points per Token": f"{Level_points_per_token}",
                "Estimated Token Price": f"$ {fdv/tsp}",
                "Estimated Tokens Airdrop": f"{Level_etimated_tokens}",
                "Estimated Airdrop Value": f"$ {Level_airdrop_value}",
                "Expected Profit": f"$ {Level_profit}",
                "Expected ROI": f"{Level_ROI} %"      
            },
            "OpenEden": {
                "Imagem": r"C:\Users\0335372\Documents\app_streamlit\open.jpg",
                "Logo": "https://pbs.twimg.com/profile_images/1529034875642478592/70m4xSFd_400x400.jpg",
                "Link": "<a href='https://portal.openeden.com/bills-campaign?refCode=1WgbBka17k' target='_blank'  style='color:#1E90FF;'>More info</a> - <a href='https://app.pendle.finance/trade/points?chains=ethereum' target='_blank'>🔗 Pendle </a>",
                "Grade": f"{Open_grade}",
                "TVL": f"{Open_tvl} M",
                "Last Update": f"{time_Open}",
                "Expiry": f"{date2.date()}",
                "Total Points Farmed": f"{round(values[0],0)}",
                "YT Multiplier": f"{round(Open_ytMul,3)}",
                "YT APY": f"{round(Open_unApy*100,2)}",
                "Time Until Expiration": f"{(date2-date1)}",
                "Protocol YT Multiplier": f"{Open_Multipleir}",
                "Protocol Referral Boost": f"{round((Open_Boost-1),2)*100} %",
                "Equivalent YT Received": f"$ {round(invested*Open_ytMul,2)}",
                "Daily Points Farmed": f"{Open_daily_pts_farmed}",
                "Total Points Farmed in YT": f"{Open_total_pts_farmed}",
                "Top 100 Concentration": f"{round(100*top100[1],2)}",
                "Total User": f"{total_users[0]}",
                "Farmed Yield in YT": f"$ {Open_farmed_yield}",
                "Mean Daily Points (x 1.30)": f"{round(Open_mean_daily,0)}",
                "Estimated Points in TGE": f"{round(Open_points_tge,0)}",
                "Points per Token": f"{Open_points_per_token}",
                "Estimated Token Price": f"$ {fdv/tsp}",
                "Estimated Tokens Airdrop": f"{Open_etimated_tokens}",
                "Estimated Airdrop Value": f"$ {Open_airdrop_value}",
                "Expected Profit": f"$ {Open_profit}",
                "Expected ROI": f"{Open_ROI} %"            
            },
            "Fragmetric": {
                "Imagem": r"C:\Users\0335372\Documents\app_streamlit\frag.jpg",
                "Logo": "https://pbs.twimg.com/profile_images/1887701999426412544/ok8QD_Gh_400x400.png",
                "Link": "<a href='https://app.fragmetric.xyz/referral?ref=77XL68' target='_blank' style='color:#1E90FF;'>More info</a> - <a href='https://app.rate-x.io/referral?ref=H9GnKZON' target='_blank'>🔗 Rate-X </a>",
                "Grade": f"{Frag_grade}",
                "TVL": f"{Frag_tvl} M",
                "Last Update": f"{time_Level}",
                "Expiry": f"{date4.date()}",
                "fragSOL Price": f"{round((fragAsUSD),2)}",
                "Equivalent Invested in fragSOL": f"{round((invested/fragAsUSD),3)}",
                "Total Points Farmed": f"{round(Frag_accured,0)}",
                "YT Multiplier": f"{round(Frag_ytMul,3)}",
                "YT APY": f"{round(Frag_unApy*100,2)}",
                "Time Until Expiration": f"{(date4-date1)}",
                "Protocol YT Multiplier": f"{Frag_Multipleir}",
                "Protocol Referral Boost": f"{round((Frag_Boost-1),2)*100} %",
                "Backpack Wallet Boost": f"{round((Backpack_Boost-1),2)*100} %",
                "Equivalent YT Received": f"$ {round(invested*Frag_ytMul,2)}",
                "Daily Points Farmed": f"{Frag_daily_pts_farmed}",
                "Total Points Farmed in YT": f"{Frag_total_pts_farmed}",
                "Top 100 Concentration": f"unknown",
                "Total User": f"{Frag_total_users}",
                "Farmed Yield in YT": f"$ {Frag_farmed_yield}",
                "Mean Daily Points (x 1.30)": f"{round(Frag_mean_daily,0)}",
                "Estimated Points in TGE": f"{round(Frag_points_tge,0)}",
                "Points per Token": f"{Frag_points_per_token}",
                "Estimated Token Price": f"$ {fdv/tsp}",
                "Estimated Tokens Airdrop": f"{Frag_etimated_tokens}",
                "Estimated Airdrop Value": f"$ {Frag_airdrop_value}",
                "Expected Profit": f"$ {Frag_profit}",
                "Expected ROI": f"{Frag_ROI} %"          
            },
            "Kyros": {
                "Imagem": r"C:\Users\0335372\Documents\app_streamlit\kyros.jpg",
                "Logo": "https://pbs.twimg.com/profile_images/1847426788252590080/-Tb-I1Yl_400x400.jpg",
                "Link": "<a href='https://boost.kyros.fi/?ref=nq3orn' target='_blank' style='color:#1E90FF;'>More info</a> - <a href='https://app.rate-x.io/referral?ref=H9GnKZON' target='_blank'>🔗 Rate-X </a>",
                "Grade": f"{Ky_grade}",
                "TVL": f"{Ky_tvl} M",
                "Last Update": f"{time_Level}",
                "Expiry": f"{date5.date()}",
                "kySOL Price": f"{round((KyAsUSD),2)}",
                "Equivalent Invested in kySOL": f"{round((invested/KyAsUSD),3)}",
                "Total Points Farmed": f"{round(Ky_accured,0)}",
                "YT Multiplier": f"{round(ky_ytMul,3)}",
                "YT APY": f"{round(Ky_unApy*100,2)}",
                "Time Until Expiration": f"{(date5-date1)}",
                "Protocol YT Multiplier": f"{Ky_Multipleir}",
                "Protocol Referral Boost": f"{round((Ky_Boost-1),2)*100} %",
                "Equivalent YT Received": f"$ {round(invested*ky_ytMul,2)}",
                "Daily Points Farmed": f"{Ky_daily_pts_farmed}",
                "Total Points Farmed in YT": f"{Ky_total_pts_farmed}",
                "Top 100 Concentration": f"{round(100*Ky_top100p,2)}",
                "Total User": f"{Ky_total_users}",
                "Farmed Yield in YT": f"$ {Ky_farmed_yield}",
                "Mean Daily Points (x 1.30)": f"{round(Ky_mean_daily,0)}",
                "Estimated Points in TGE": f"{round(Ky_points_tge,0)}",
                "Points per Token": f"{Ky_points_per_token}",
                "Estimated Token Price": f"$ {fdv/tsp}",
                "Estimated Tokens Airdrop": f"{Ky_etimated_tokens}",
                "Estimated Airdrop Value": f"$ {Ky_airdrop_value}",
                "Expected Profit": f"$ {Ky_profit}",
                "Expected ROI": f"{Ky_ROI} %"   
            }
        }
        print(protocolos)
        
    # --- Salvar automaticamente sem botão ---
    salvar_json(protocolos)

    # --- Estado de seleção ---
    if "protocolo_selecionado" not in st.session_state:
        st.session_state.protocolo_selecionado = None
    if st.session_state.protocolo_selecionado:
        # Mostrar detalhes do protocolo selecionado
        p = st.session_state.protocolo_selecionado
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(
                f"""
                <div style="
                    border: 3px solid white;
                    border-radius: 10px;
                    padding: 10px;
                    background-color: #342b44;
                    color: white;
                    margin-bottom: 5px;
                ">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 5px;font-size: 22px;">
                        <img src="{protocolos[p]['Logo']}" width="70" height="70" style="border-radius: 5%;">
                        <h4 style="margin: 5;color: #FFA500">{p}</h4>
                    </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(f"""
            <div style="background-color: #376a94; padding: 20px; border: 2px solid white; border-radius: 10px; margin-top: 20px; font-size: 16px;margin-bottom: 5px;">
                <h2>Details {p}</h2>
                    <p style="font-size:22px;">
                        <strong>Protocol:</strong> {p} – 
                        <a href="{protocolos[p]['Link']}" target="_blank" style="color:#FFA500;">
                            {protocolos[p]['Link']}
                        </a>
                    </p>
                <ul>
                    <li><strong>TVL:</strong> {protocolos[p]['TVL']}</li>
                    <li><strong>Total Points Farmed:</strong> {protocolos[p]['Total Points Farmed']} XP</li>
                    <li><strong>Last Update:</strong> {protocolos[p]['Last Update']}</li>
                    <li><strong>YT Multiplier:</strong> {protocolos[p]['YT Multiplier']} x</li>
                    <li><strong>YT APY:</strong> {protocolos[p]['YT APY']}</li>
                    <li><strong>Time Until YT Expiration:</strong> {protocolos[p]['Time Until Expiration']}</li>
                    <li><strong>Protocol YT Multiplier:</strong> {protocolos[p]['Protocol YT Multiplier']}</li>
                    <li><strong>Protocol Referral Boost:</strong> {protocolos[p]['Protocol Referral Boost']}</li>
                    <li><strong>Equivalent YT Received:</strong> {protocolos[p]['Equivalent YT Received']}</li>
                    <li><strong>Daily Points Farmed:</strong> {protocolos[p]['Daily Points Farmed']} XP</li>
                    <li><strong>Total Points Farmed in YT Expiration:</strong> {protocolos[p]['Total Points Farmed in YT']} XP</li>
                    <li><strong>Top 100 Points Percentual Concentration:</strong> {protocolos[p]['Top 100 Concentration']}%</li>
                    <li><strong>Total Users:</strong> {protocolos[p]['Total User']}</li>
                    <li><strong>Farmed Yield in YT Expiration:</strong> {protocolos[p]['Farmed Yield in YT']}</li>
                    <li><strong>Mean Daily Points (x1.30):</strong> {protocolos[p]['Mean Daily Points (x 1.30)']} XP</li>
                    <li><strong>Estimated Total Points in TGE:</strong> {protocolos[p]['Estimated Points in TGE']} XP</li>
                    <li><strong>Points to Receive 1 Token:</strong> {protocolos[p]['Points per Token']}</li>
                    <li><strong>Estimated Token Price:</strong> {protocolos[p]['Estimated Token Price']}</li>
                    <li><strong>Estimated Tokens Airdrop:</strong> {protocolos[p]['Estimated Tokens Airdrop']}</li>
                    <li><strong>Estimated Airdrop Value:</strong> {protocolos[p]['Estimated Airdrop Value']}</li>
                    <li><strong>Expected Profit:</strong> {protocolos[p]['Expected Profit']}</li>
                    <li><strong>Expected ROI:</strong> {protocolos[p]['Expected ROI']}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🔙 Return"):
            st.session_state.protocolo_selecionado = None

    else:
        st.markdown("<h3 style='text-align: center;'></h3>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)

        cols = [col1, col2, col3, col4]
        i = 0

        for p in protocolos:#<img src="{protocolos[p]['Imagem']}" width="200"/>
            with cols[i % 4]:
                col_left, col_center, col_right = st.columns([1, 2, 1])
                with col_center:
                    st.image(protocolos[p]['Imagem'], width=600) 
                st.markdown(f"""
                    <div style='text-align: center; font-size: 24px;'>
                        <p>TVL: {protocolos[p]['TVL']}</p>
                        <p>Expected ROI: {protocolos[p]['Expected ROI']}</p>
                        <p>YT Multiplier: {protocolos[p]['YT Multiplier']}</p>
                        <p>Boost: {protocolos[p]['Protocol Referral Boost']}</p>
                        <p>{protocolos[p]['Expiry']}</p>
                        <p>{protocolos[p]['Grade']}</p>
                        <p></p>
                    </div>
                """, unsafe_allow_html=True)
                bcol1, bcol2 = st.columns([2, 2.6])
                with bcol2:
                    if st.button(f"View Details", key=p):
                        st.session_state.protocolo_selecionado = p
            i += 1
elif opcao == "Pendle APY Prediction":
    markets = get_pendle_markets()
    print(markets)
    names = markets["name"].tolist()
    exp = markets["expiry"].str.split('T').str[0].tolist()

    # Criar rótulos combinando nome + data
    markets["label"] = markets["name"] + " (Expires in: " + exp + ")"
    print(markets)
    # Exibindo a lista de seleção múltipla
    #selected_names = st.multiselect("Escolha um ou mais mercados", options)

    st.sidebar.markdown("<h3 style='font-size: 20px;'>Select Pendle Market</h3>", unsafe_allow_html=True)
    with st.sidebar.expander("", expanded=True):
        # CSS para alterar a fonte de todos os selectbox
        st.markdown("""
            <style>
            div[data-baseweb="select"] {
                font-size: 18px;
            }
            </style>
        """, unsafe_allow_html=True)
        # Selectbox exibindo as labels
        selected_label = st.selectbox(
            "Markets:",
            markets["label"].tolist(),
            format_func=lambda x: x.upper()
        )    
        time_scale = st.selectbox(
            "Time in:",
            ["hour", "day"],
            format_func=lambda x: x.upper()
        )

    # Pega o mercado selecionado com base no label
    selected_row = markets[markets["label"] == selected_label].iloc[0]
    # Pegando o address
    if not selected_row.empty:
        address = selected_row["address"]
        label = selected_row["label"]
        expires = selected_row["expiry"]
        st.markdown(f"<span style='font-size:22px'><strong>Selected Market:</strong> {label}</span>", unsafe_allow_html=True)
    else:
        st.markdown("Maket not Founded")
    print(address)
    with st.spinner('Loading Pendle Data to Plot Implied APY Tendency...'):
        df_implied,implied_apy,base_apy,tvl_in_k,trend_line,upper_line,lower_line,trend_line_extended,upper_line_extended,lower_line_extended,dates,extended_dates,expiry_date,address = get_pendle_apy_data(selected_row,time_scale)

        # Supondo que base_apy seja uma lista ou Series
        base_apy_series = pd.Series(base_apy)

        # Calcular Q1, Q3 e IQR
        Q1 = base_apy_series.quantile(0.1)
        Q3 = base_apy_series.quantile(0.9)
        IQR = Q3 - Q1

        # Definir limites
        lower_bound = Q1 - 1 * IQR
        upper_bound = Q3 + 1 * IQR

        # Filtrar dados válidos
        mask = (base_apy_series >= lower_bound) & (base_apy_series <= upper_bound)
        filtered_dates = [d for d, keep in zip(dates, mask) if keep]
        filtered_base_apy = base_apy_series[mask].tolist()

        # Criar figura
        fig = go.Figure()

        # Base e Implied APY
        fig.add_trace(go.Scatter(x=filtered_dates, y=filtered_base_apy, mode='lines+markers', name='Base APY', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=dates, y=implied_apy, mode='lines+markers', name='Implied APY', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=dates, y=trend_line, mode='lines', name='Implied APY Tendency', line=dict(color='black', dash='dash')))
        fig.add_trace(go.Scatter(x=dates, y=upper_line, mode='lines', name='Maximum Implied APY Tendency', line=dict(color='red', dash='dash')))
        fig.add_trace(go.Scatter(x=dates, y=lower_line, mode='lines', name='Minimum Implied APY Tendency', line=dict(color='#3cb371', dash='dash')))
        fig.add_trace(go.Scatter(x=extended_dates, y=trend_line_extended[-len(extended_dates):], mode='lines', name='Tendency up to Expire', line=dict(color='black', dash='dot')))
        fig.add_trace(go.Scatter(x=extended_dates, y=upper_line_extended[-len(extended_dates):], mode='lines', name='Maximum Tendency up to Expire', line=dict(color='red', dash='dot')))
        fig.add_trace(go.Scatter(x=extended_dates, y=lower_line_extended[-len(extended_dates):], mode='lines', name='Minimum Tendency up to Expire', line=dict(color='green', dash='dot')))
        #fig.add_trace(go.Scatter(x=df_forecast['date'], y=df_forecast['forecast_ap'], mode='lines', name='Implied APY Prediction', line=dict(color='orange', dash='dash')))

        # TVL em eixo secundário
        fig.add_trace(go.Scatter(x=dates, y=tvl_in_k, mode='lines+markers', name='TVL (Mi USD)', line=dict(color='orange', dash='dot'), yaxis='y2'))

        # Linha vertical para expiry (usar apenas add_shape + add_annotation)
        fig.add_shape(
            type='line',
            x0=expiry_date,
            x1=expiry_date,
            y0=0,
            y1=1,
            line=dict(color='gray', dash='dot'),
            xref='x',
            yref='paper'
        )
        fig.add_annotation(
            x=expiry_date,
            y=0,
            text='Expiry Date',
            showarrow=False,
            xanchor='left',
            yanchor='bottom',
            xref='x',
            yref='paper',
            font=dict(color='red')
        )

        # Layout com dois eixos y
        fig.update_layout(
            title=f'    YT-{selected_row["name"]} {expiry_date.date()} - History of Base APY, Implied APY, Tendency Lines and TVL',
            xaxis=dict(title='Date'),
            yaxis=dict(title='APY (%)',range=[0, None]),
            yaxis2=dict(title='TVL (Mi USD)', overlaying='y', side='right'),
            legend=dict(
                x=1,              # posição horizontal (0 = esquerda)
                y=1,              # posição vertical (1 = topo)
                xanchor='right',   # ancora horizontal da legenda
                yanchor='top',    # ancora vertical da legenda
                bgcolor='rgba(52,43,68,0.8)'  # fundo semi-transparente opcional
            ),
            plot_bgcolor='rgba(255, 255, 255, 1)',   # Cor do fundo da área do gráfico
            paper_bgcolor='rgba(52,43,68, 1)',  # Cor do fundo geral da figura
            hovermode='x unified',
            height=600
        )

        # Mostrar com zoom habilitado
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
    """
    <style>
    .pendle-apy-description {
        font-size: 22px;
        line-height: 1.6;
        text-align: justify;
    }
    </style>

    <div class="pendle-apy-description">

    <h3>📈 How the Pendle APY Chart Works?</h3>

    <p>
    The APY (Annual Percentage Yield) chart on Pendle shows the evolution of annualized yield rates for tokenized assets over time.
    It is built with multiple layers of information to support deeper analysis:
    </p>

    <ul>
        <li><strong>Base APY</strong>: This reflects the base yield from the underlying protocol (e.g., Aave, Compound), excluding any incentive rewards.</li>
        <li><strong>Implied APY</strong>: This is the market-implied yield calculated from the price of the YT (Yield Token). It represents the market's expectation of future returns up to the maturity date.</li>
        <li><strong>Trend Line</strong>: A trend line is applied to the Implied APY, helping to visualize the general direction of expected yields—whether they are increasing, decreasing, or stable.</li>
        <li><strong>TVL (Total Value Locked)</strong>: Displayed on a secondary axis, it shows how much value is allocated to the asset, giving insight into investor interest over time.</li>
    </ul>

    <p>
    In addition, <strong>buying opportunities</strong> may arise when the Implied APY touches the <span style='color:black;'><strong>minimum green trend line</strong></span>,
    indicating a temporary undervaluation. Conversely, <strong>selling opportunities</strong> may be more favorable when the Implied APY reaches the <span style='color:black;'><strong>maximum red trend line</strong></span>,
    suggesting a potential overvaluation.
    </p>

    <p>
    This chart allows users to compare real and expected yields, monitor market sentiment, and identify attractive entry and exit points for Pendle pools.
    </p>

    </div>
    """,
    unsafe_allow_html=True
    )


    
elif opcao == "Latest Airdrops":
    st.info("🚧 Coming Soon: Protocols with Airdrop Potential.")

elif opcao == "Depin Airdrops":
    st.info("🚧 Coming Soon: DePIN Protocols with Airdrops.")

elif opcao == "Comparative YT Table":

    st.markdown(
        """
        <style>
        .bridge-description {
            font-size: 22px;
            text-align: justify;
            line-height: 1.6;
        }
        </style>

        <div class="bridge-description">
            Comparative table of the protocols presented in the ‘Farm with YT’ Section. You can dowload the table.
        </div>
        """,
        unsafe_allow_html=True
    )

    df = pd.DataFrame({
        "Protocolo": list(protocolos.keys()),
        "TVL": [protocolos[p]["TVL"] for p in protocolos],
        "Total Points Farmed (XP)": [protocolos[p]["Total Points Farmed"] for p in protocolos],
        "Last Update": [protocolos[p]["Last Update"] for p in protocolos],
        "YT Multiplier (x)": [protocolos[p]["YT Multiplier"] for p in protocolos],
        "YT APY": [protocolos[p]["YT APY"] for p in protocolos],
        "Time Until YT Expiration": [protocolos[p]["Time Until Expiration"] for p in protocolos],
        "Protocol YT Multiplier": [protocolos[p]["Protocol YT Multiplier"] for p in protocolos],
        "Protocol Referral Boost": [protocolos[p]["Protocol Referral Boost"] for p in protocolos],
        "Equivalent YT Received": [protocolos[p]["Equivalent YT Received"] for p in protocolos],
        "Daily Points Farmed (XP)": [protocolos[p]["Daily Points Farmed"] for p in protocolos],
        "Total Points in YT Expiration (XP)": [protocolos[p]["Total Points Farmed in YT"] for p in protocolos],
        "Top 100 Concentration (%)": [protocolos[p]["Top 100 Concentration"] for p in protocolos],
        "Total Users": [protocolos[p]["Total User"] for p in protocolos],
        "Farmed Yield in YT": [protocolos[p]["Farmed Yield in YT"] for p in protocolos],
        "Mean Daily Points (XP)": [protocolos[p]["Mean Daily Points (x 1.30)"] for p in protocolos],
        "Points in TGE (XP)": [protocolos[p]["Estimated Points in TGE"] for p in protocolos],
        "Points per Token": [protocolos[p]["Points per Token"] for p in protocolos],
        "Token Price": [protocolos[p]["Estimated Token Price"] for p in protocolos],
        "Tokens Airdrop": [protocolos[p]["Estimated Tokens Airdrop"] for p in protocolos],
        "Airdrop Value": [protocolos[p]["Estimated Airdrop Value"] for p in protocolos],
        "Profit": [protocolos[p]["Expected Profit"] for p in protocolos],
        "ROI": [protocolos[p]["Expected ROI"] for p in protocolos],
        "Rating": [protocolos[p]["Grade"] for p in protocolos],  # Se estiver disponível
        "Expiry": [protocolos[p]["Expiry"] for p in protocolos]  # Se aplicável
    })
    dfT = df.set_index("Protocolo").T
    styled_dfT = (
        dfT.style
        .applymap(lambda v: 'color: green' if isinstance(v, (int, float)) and v > 0.1 else 'color: #342b44')
        .set_table_styles([
            {
                "selector": "th.row_heading", 
                "props": [("color", "white"), ("background-color", "#342b44"), ("font-weight", "bold"), ("font-size", "20px")]
            },
            {
                "selector": "th.col_heading", 
                "props": [("color", "white"), ("background-color", "#342b44"), ("font-weight", "bold"), ("font-size", "20px")]
            },
            {
                "selector": "td",  # Aqui é o corpo da tabela
                "props": [("font-size", "18px"), ("padding", "6px 12px"),("font-weight", "bold")]
            }
        ])
    )
    #st.write(styled_dfT)
    # Mostrando no Streamlit
    #st.dataframe(df, use_container_width=True)
    styled_df = df.style.applymap(lambda v: 'color: green' if isinstance(v, (int, float)) and v > 0.1 else 'color: #342b44')

    st.markdown("""
    <style>
    /* Fonte e cor das abas */
    .stTabs [data-baseweb="tab"] {
        font-size: 20px;
        font-family: 'Segoe UI', sans-serif;
        color: white;
        background-color: #342b44;  /* roxo escuro */
        border-radius: 8px 8px 0 0;
        padding: 8px;
        margin-right: 2px;
    }

    /* Aba ativa */
    .stTabs [aria-selected="true"] {
        background-color: #FFA500 !important;  /* laranja */
        color: black !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
   
    tab1, tab2 = st.tabs(["📄 Vertical Table","🔁 Horizontal Table"])

    with tab1:
        st.markdown("<h2 style='font-size:32px;'>Vertical Table</h2>", unsafe_allow_html=True)
        st.markdown(styled_dfT.to_html(), unsafe_allow_html=True)

    with tab2:
        st.markdown("<h2 style='font-size:32px;'>Horizontal Table</h2>", unsafe_allow_html=True)
        st.write(styled_df)

elif opcao == "Bridges & Swaps Protocols":
    # Updated protocols data including Sonic and Hyperlane networks

    st.markdown(
        """
        <style>
        .bridge-description {
            font-size: 22px;
            text-align: justify;
            line-height: 1.6;
        }
        </style>

        <div class="bridge-description">
            Explore and access the best bridge and swap protocols available for each network, 
            making it easier and more secure to transfer and exchange assets within the crypto ecosystem.
        </div>
        """,
        unsafe_allow_html=True
    )

    protocols_bridge_swap = {
        "EVM": [
            {"name": "Relay", "site": "https://relay.link/bridge/", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1753515078316355584/uT6CssGo_400x400.jpg"},
            {"name": "Jumper Exchange", "site": "https://jumper.exchange", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1889316674383282176/ulV41xZ7_400x400.jpg"},
            {"name": "Uniswap", "site": "https://uniswap.org", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1831348758753206272/y2Z0hMrl_400x400.jpg"},
            {"name": "Swaps.io", "site": "https://swaps.io?ref=q7kMylhY2EY", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1710931572667584512/GWMzqBE0_400x400.png"},
            {"name": "Bungee", "site": "https://bungee.exchange", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1883923855456215040/uUFkZI_D_400x400.jpg"},
            {"name": "SuperBridge", "site": " https://superbridge.app/", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1891417040399048705/g_qJg56l_400x400.jpg"},
            {"name": "Comet", "site": "https://cometbridge.app/?", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1771071398251012096/Fe_n9mbm_400x400.jpg"},
            {"name": "iZumi Finance", "site": "https://izumi.finance", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1509704804032937991/5qVVZwJj_400x400.jpg"},
            {"name": "OkuTrade", "site": "https://oku.trade", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1877565663125913600/x6HqqFJf_400x400.jpg"},
            {"name": "Odos", "site": "https://app.odos.xyz/", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1917255155717693440/qysV1uvu_400x400.jpg"},
            {"name": "Synapse", "site": "https://synapseprotocol.com", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1692635184837836800/uZB0CnEG_400x400.jpg"},
            {"name": "Gas.zip", "site": "https://lz.gas.zip/", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1750310657680101376/HEtUyTZy_400x400.jpg"}, 
            {"name": "LayerSwap", "site": "https://layerswap.io/app", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1635993072327639041/G_YIQ-G1_400x400.jpg"},      
            {"name": "SushiSwap", "site": "https://www.sushi.com/sonic/swap",  "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1848386042073858048/Dev1DVpq_400x400.jpg"},
            {"name": "KyberSwap", "site": "https://kyberswap.com/swap/sonic",  "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1641706567014940672/UFuWgdxn_400x400.jpg"},    
            {"name": "SquidRouter", "site": "https://app.squidrouter.com", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1548647667135291394/W2WOtKUq_400x400.jpg"},
            {"name": "Stargate", "site": "https://stargate.finance", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1453865643053182980/s9_nNOkD_400x400.jpg"},
            {"name": "Hyperlane", "site": "https://hyperlane.xyz", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1671589406816313345/wGzRPeEf_400x400.jpg"}, 
            {"name": "Merkly", "site": "https://minter.merkly.com/hyperlane/token", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1730147960082628608/3Oz6434E_400x400.jpg"},
            {"name": "Across Protocol", "site": "https://app.across.to/bridge?", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1886903904874512384/wnRMhfef_400x400.jpg"},
            {"name": "Rhino.fi", "site": "https://app.rhino.fi/bridge?", "fees": "High", "image": "https://pbs.twimg.com/profile_images/1715027429989773312/WDP-gVnU_400x400.jpg"},
            {"name": "Retro", "site": "https://app.retrobridge.io/", "fees": "High", "image": "https://pbs.twimg.com/profile_images/1764776304895787009/TqIDlj_P_400x400.jpg"},
            {"name": "Orbiter Finance", "site": "https://www.orbiter.finance/?channel=0xa786817be0b3fc4385e9f93140b513c9846c6f74", "fees": "High", "image": "https://pbs.twimg.com/profile_images/1880886737221664768/_uBH9pgt_400x400.jpg"},
            {"name": "Owlto", "site": "https://owlto.finance/?ref=0xa786817bE0B3FC4385E9F93140B513c9846C6f74", "fees": "Very High", "image": "https://pbs.twimg.com/profile_images/1886736859054923778/Iv098oCX_400x400.jpg"},
            {"name": "deBridge", "site": "https://debridge.finance", "fees": "Very High", "image": "https://pbs.twimg.com/profile_images/1894665537466040320/5vQrjq6M_400x400.jpg"},
        ],
        "Solana": [
            {"name": "Jupiter", "site": "https://jup.ag", "fees": "Low", "image": "https://jup.ag/favicon.ico"},
            {"name": "Kamino", "site": "https://swap.kamino.finance/swap/", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1800478667040002048/8bUg0jRH_400x400.jpg"},
            {"name": "Orca", "site": "https://www.orca.so/", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1898099113859678208/1NOETPA8_400x400.png"},
            {"name": "Stabble", "site": "https://app.stabble.org/?referrer=fleming25", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1876267708238434304/8J3u2h6I_400x400.jpg"},
            {"name": "Portal Bridge", "site": "https://portalbridge.com", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1511707234329313281/QJXH-NcS_400x400.jpg"},
            {"name": "Mayan", "site": "https://swap.mayan.finance/", "fees": "High", "image": "https://pbs.twimg.com/profile_images/1891499635597856769/5BMo_JQJ_400x400.jpg"},
            {"name": "Orbiter Finance", "site": "https://www.orbiter.finance/?channel=0xa786817be0b3fc4385e9f93140b513c9846c6f74", "fees": "High", "image": "https://pbs.twimg.com/profile_images/1880886737221664768/_uBH9pgt_400x400.jpg"},
            {"name": "Owlto", "site": "https://owlto.finance/?ref=0xa786817bE0B3FC4385E9F93140B513c9846C6f74", "fees": "Very High", "image": "https://pbs.twimg.com/profile_images/1886736859054923778/Iv098oCX_400x400.jpg"},
            {"name": "deBridge", "site": "https://debridge.finance", "fees": "Very High", "image": "https://pbs.twimg.com/profile_images/1894665537466040320/5vQrjq6M_400x400.jpg"},
        ],
        "Sui": [
            {"name": "Bridge.sui", "site": "https://bridge.sui.io/", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1893074983095803904/kgAhTMQP_400x400.jpg"},
            {"name": "Aftermath (Sui)", "site": "https://aftermath.finance/trade?", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1898807230818078720/g20J2FLu_400x400.jpg"},
            {"name": "7k (Sui)", "site": "https://7k.ag/?ref=6ZG45VKF2W", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1874009441676517380/THiznWPv_400x400.jpg"},
            {"name": "Portal Bridge", "site": "https://portalbridge.com", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1511707234329313281/QJXH-NcS_400x400.jpg"},
        ],
        "Bitcoin": [   
            {"name": "Swaps.io", "site": "https://swaps.io?ref=q7kMylhY2EY", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1710931572667584512/GWMzqBE0_400x400.png"},
            {"name": "Meson", "site": "https://meson.fi/", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1844573068083273728/03OqXzZD_400x400.jpg"},
            {"name": "Oooo Money", "site": "https://bridge.oooo.money/", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1749633878460084224/yduMtwPo_400x400.jpg"},     
            {"name": "Bitcow", "site": "https://threshold.network", "fees": "High", "image": "https://pbs.twimg.com/profile_images/1770659692915933184/x8sdW6p3_400x400.jpg"},
            {"name": "Orbiter Finance", "site": "https://www.orbiter.finance/?channel=0xa786817be0b3fc4385e9f93140b513c9846c6f74", "fees": "High", "image": "https://pbs.twimg.com/profile_images/1880886737221664768/_uBH9pgt_400x400.jpg"},
            {"name": "Owlto", "site": "https://owlto.finance/?ref=0xa786817bE0B3FC4385E9F93140B513c9846C6f74", "fees": "Very High", "image": "https://pbs.twimg.com/profile_images/1886736859054923778/Iv098oCX_400x400.jpg"},
        ],
        "Eclipse": [
            {"name": "Relay", "site": "https://relay.link/bridge/", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1753515078316355584/uT6CssGo_400x400.jpg"},
            {"name": "Invariant", "site": "https://eclipse.invariant.app/points", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1842564007770693632/pW6YmToL_400x400.jpg"},
            {"name": "Orca", "site": "https://www.orca.so/", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1898099113859678208/1NOETPA8_400x400.png"},
            {"name": "Eclipse Bridge", "site": "https://app.eclipse.xyz/bridge?target=deposit", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1816156021519466496/FBQWKnR4_400x400.jpg"},     
            {"name": "Retro", "site": "https://app.retrobridge.io/", "fees": "High", "image": "https://pbs.twimg.com/profile_images/1764776304895787009/TqIDlj_P_400x400.jpg"},
        ],
        "Cosmos": [
            {"name": "Osmosis", "site": "https://app.osmosis.zone", "fees": "Low", "image": "https://app.osmosis.zone/favicon.ico"},
            {"name": "Axelar", "site": "https://axelar.network", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1869486848646537216/rs71wCQo_400x400.jpg"},
            {"name": "Skip.go", "site": "https://go.skip.build/", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1910278053340823552/xl3wZv0N_400x400.png"},
        ],
        "Celestia": [
            {"name": "Hyperlane", "site": "https://hyperlane.xyz", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1671589406816313345/wGzRPeEf_400x400.jpg"}, 
            {"name": "Injective Bridge", "site": "https://hub.injective.network/bridge", "fees": "Fair", "image": "https://injective.com/favicon.ico"},
            {"name": "Skip.go", "site": "https://go.skip.build/", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1910278053340823552/xl3wZv0N_400x400.png"},
        ],
        "Injective": [
            {"name": "Hyperlane", "site": "https://hyperlane.xyz", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1671589406816313345/wGzRPeEf_400x400.jpg"},  
            {"name": "Skip.go", "site": "https://ibcprotocol.org", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1910278053340823552/xl3wZv0N_400x400.png"},
            {"name": "Helix", "site": "https://helixapp.com/swap/", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1557766092088610816/ZPpcNEAd_400x400.jpg"},
        ],
        "Mantle": [
            {"name": "iZumi Finance", "site": "https://izumi.finance", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1509704804032937991/5qVVZwJj_400x400.jpg"},
            {"name": "Odos", "site": "https://app.odos.xyz/", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1917255155717693440/qysV1uvu_400x400.jpg"},
            {"name": "Merchant Moe", "site": "https://merchantmoe.com/trade", "fees": "Low", "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAkFBMVEVHcEztgKftgKftgKftgKftgKftgKftgaXtgKftgKftgKftgKjtgafugKftgKfwgan1g6sOKUUDGzcBKUoBIkAENFLgfZwFQmYXOFlBRURxWTwAN1stMDrXgIWObFAZJjF+YD9nU1GbYW4WMEshR2pBRmDJe3exaoVyVnFgTjviho5DU3q1d2iTY4pcR2UAAiuOwOJGAAAADnRSTlMAYd8/hTLv/urEFxc/PxM4j74AAAE7SURBVCiRjZPpdoIwEIWjAgK2k0ASwiag4r70/d+ukwS0pPWc3l+cfGfmzgYho3wvCgHCyPOJq1kATwWzCVrNYaL56sU+pggowGJkC5etL3SkscPYjRdrCjaz40ePJa8aBnNTpxMIRcHzYgmgaw6miN3PdZJLdA2wdycuk2Wb5BWagk+80Yoxhg/Q8zJFeMBvj0QDOp72jzuwkxQaKg0jEtqu90pyIdKHSnYIq/0FX0NiA68y3yVJkvZSdC2vNpl2AAPpXe0My3nd1WlxM+4IdVp27ZGJlBdN+dVulxZhWlOQ6hGlm+4sELGxq0i3QrNK1WV3rgUO9Yl0K3oImWrQSnA5FDLIN+NjTWvQgf1kgR08XTen7TGbIDt4vTIzuymyK/u17EHx32di9PaIUJ+v84vd04z/e9RvfodvzdYp0ob0q0QAAAAASUVORK5CYII="},
            {"name": "Orbiter Finance", "site": "https://www.orbiter.finance/?channel=0xa786817be0b3fc4385e9f93140b513c9846c6f74", "fees": "High", "image": "https://pbs.twimg.com/profile_images/1880886737221664768/_uBH9pgt_400x400.jpg"},
        ],
        "Monad": [
            {"name": "Jumper Exchange", "site": "https://jumper.exchange",  "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1889316674383282176/ulV41xZ7_400x400.jpg"},
            {"name": "Relay", "site": "https://relay.link/bridge",  "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1753515078316355584/uT6CssGo_400x400.jpg"},
            {"name": "TimeSwap", "site": "https://timeswap.io/",  "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1879076220106678272/ZkkhrcyV_400x400.jpg"},
        ],
        "Sonic Labs": [
            {"name": "SushiSwap", "site": "https://www.sushi.com/sonic/swap",  "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1848386042073858048/Dev1DVpq_400x400.jpg"},
            {"name": "KyberSwap", "site": "https://kyberswap.com/swap/sonic",  "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1641706567014940672/UFuWgdxn_400x400.jpg"},    
            {"name": "Swapx", "site": "https://swapx.fi/",  "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1896588709870317568/fj3naflX_400x400.jpg"},        
            {"name": "Sonic", "site": "https://gateway.soniclabs.com/ethereum/sonic/ftm-s",  "fees": "High", "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAA8FBMVEVHcEzRWCHmjUHlWhRNZIT1hzD1hC8tT298aGoeP1j8t1cnUoErV4khRGJEYocfQFkcO05saHQcO0+jYEb7rE/4nkT9vVz9wF6xXTuxXTv9vl39vl0UFBYBDBQABBMmTHEeP1gTEhQREA8oU4AbL0MSDAUjRWRqZ3PNVyHbVhZEYohSaYYBBQmJZV79sFKNVUHCXTArWYw2Xopea4AgJC12UEaaZVSrWzlONjH0bx3mWxP3Xg4nGhfBUhpgVFngfS9xW1r8oUT5kDeqY0liOib1fyqBTCe5aTu0VClmMBqcPxYOCwg7Sl5hbYTsl0FEIRWX2w4JAAAAHHRSTlMAdDPpdRlCOvrp7BnjGe9iwsKG6WPih/zDwsPCZvwGfwAAAUpJREFUKJF9k+eWgkAMhcdetvdGZuiCIqALFopi7/r+b7ODqHvW9Uz+zfnOzSQ3CULHSKfen1r14kO2gM4jldHs9ojCynftNvsH5TKeTqHlulFlU6s2r69+Wb7re/o8ABqG4ayrzYZ0yp2fdP1lqC2Ai0NYiWpDIgeaG066Cxxo9jihHKfIEiE3e/hCYQgQ2LOxcaSOREoxex4Mp6Gv7yBoj1wQE7qSiXpHYXnQx3jpe0vAVqvuGEKi5VUqTZsD+hfsQt2eCp16scetYiw4Kl9Ar+YW0wfAYj4buZ1eZbPmFDGW8o/o05zhfSLAHStxqEpkUVFk/h6VzSnGOO4fsAFUSSE1QZVlvoTezG2/7+m6Fs7blhVFB0iIyvMnGF6CzLRfp4Lgf0HMVpgmMO27bLx4MP7SyMTjyNjDZq4Je8HYq8le6uQcPs7P4QdCT2YBNL5ZPgAAAABJRU5ErkJggg=="},
            {"name": "deBridge", "site": "https://debridge.finance",  "fees": "Very High", "image": "https://pbs.twimg.com/profile_images/1894665537466040320/5vQrjq6M_400x400.jpg"},
        ],
        "Hyperliquid":[
            {"name": "HyperSwap", "site": "https://app.hyperswap.exchange/#/swap?referral=Fleming",  "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1818300103825719296/mE6pjX1x_400x400.jpg"},
            {"name": "TimeSwap", "site": "https://timeswap.io/",  "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1879076220106678272/ZkkhrcyV_400x400.jpg"},
        ]
    }
    st.sidebar.markdown("<h3 style='font-size: 20px;'>Select Network</h3>", unsafe_allow_html=True)
    with st.sidebar.expander("", expanded=True):
        # CSS para alterar a fonte de todos os selectbox
        st.markdown("""
            <style>
            div[data-baseweb="select"] {
                font-size: 20px;
            }
            </style>
        """, unsafe_allow_html=True)
        selected_network = st.selectbox(
            "",
            list(protocols_bridge_swap.keys()),
            format_func=lambda x: x.upper()
        )
    # Style setup
    st.markdown("""
        <style>
            body {background-color: #c3a9a5;}
            .title-style {
                font-size: 36px;
                font-weight: bold;
                color: #fbd46d;
                margin-bottom: 5px;
            }
            .card {
                border: 3px solid white;
                border-radius: 10px;
                padding: 10px;
                background-color: #2c4a6b;
                color: white;
                margin: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Network selection
    #selected_network = st.selectbox("Select a network:", list(protocols_bridge_swap.keys()), format_func=lambda x: x.upper())

    # Render selected network section
    
    st.subheader(selected_network.upper())
    cols = st.columns(4)
    for idx, protocol in enumerate(protocols_bridge_swap[selected_network]):
        with cols[idx % 4]:
            st.markdown(
                f"""
                <div style="
                    border: 3px solid white;
                    border-radius: 10px;
                    padding: 10px;
                    background-color: #342b44;
                    color: white;
                    margin-bottom: 5px;
                    margin-top: 20px;
                ">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 5px; margin-bottom: 5px;">
                        <img src="{protocol['image']}" width="50" height="50" style="border-radius: 50%;">
                        <h4 style="margin: 0;color: #FFA500">{protocol['name']}</h4>
                    </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(f"""
                <div style="
                        border: 2px solid white;
                        border-radius: 10px;
                        padding: 20px;
                        background-color: #376a94;
                        color: white;
                        margin-bottom: 5px;
                    ">
                        <div style="margin-top: 20px; font-size: 20x;">
                            <p style="font-size: 20px;">💸 Fees: {protocol['fees']} </p>
                            <p style="font-size: 20px;">🌐 Site: <a href="{protocol['site']}" style="color: lightblue; font-size: 20px;" target="_blank">Visit Protocol</a></p>
                        </div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown(
        "<hr style='border: 2px double #342b44;'>",
        unsafe_allow_html=True
    )

elif opcao == "Revoke Contract":

    st.markdown(
        """
        <style>
        .bridge-description {
            font-size: 22px;
            text-align: justify;
            line-height: 1.6;
        }
        </style>

        <div class="bridge-description">
            <p>The purpose of revoke protocols is to allow you to remove permissions previously granted to smart contracts in your cryptocurrency wallet.</p>
            <p>When interacting with DApps (such as exchanges, farms, or NFTs), you typically authorize these contracts to move your tokens — and these permissions remain active indefinitely unless you revoke them manually.</p>
            <p>This provides more control and security, as revoking these permissions ensures that malicious or compromised contracts cannot move your assets without your consent.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    protocols_revoke= {
        "EVM": [
            {"name": "Revoke Cash", "site": "https://revoke.cash/", "image": "https://pbs.twimg.com/profile_images/1884991661043859456/7avxjsrH_400x400.jpg"},
            {"name": "De.Fi Shield", "site": "https://de.fi/shield", "image": "https://pbs.twimg.com/profile_images/1896908731180359680/WoOKUzJ5_400x400.jpg"},
        ],
        "SOLANA": [
            {"name": "Famous Foxes", "site": "https://famousfoxes.com/revoke",  "image": "https://pbs.twimg.com/profile_images/1433087419046367235/uFYaQEsU_400x400.jpg"},
            {"name": "Solrevoker", "site": "https://solrevoker.com/", "image": "https://pbs.twimg.com/profile_images/1877702623014580224/t9mvXaqU_400x400.jpg"},
        ],
    }
    st.sidebar.markdown("<h3 style='font-size: 20px;'>Select Network</h3>", unsafe_allow_html=True)
    with st.sidebar.expander("", expanded=True):
        # CSS para alterar a fonte de todos os selectbox
        st.markdown("""
            <style>
            div[data-baseweb="select"] {
                font-size: 20px;
            }
            </style>
        """, unsafe_allow_html=True)
        selected_network = st.selectbox(
            "",
            list(protocols_revoke.keys()),
            format_func=lambda x: x.upper()
        )
    # Style setup
    st.markdown("""
        <style>
            body {background-color: #c3a9a5;}
            .title-style {
                font-size: 36px;
                font-weight: bold;
                color: #fbd46d;
                margin-bottom: 5px;
            }
            .card {
                border: 3px solid white;
                border-radius: 10px;
                padding: 10px;
                background-color: #2c4a6b;
                color: white;
                margin: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Network selection
    #selected_network = st.selectbox("Select a network:", list(protocols_bridge_swap.keys()), format_func=lambda x: x.upper())

    # Render selected network section
    
    st.subheader(selected_network.upper())
    cols = st.columns(4)
    for idx, protocol in enumerate(protocols_revoke[selected_network]):
        with cols[idx % 4]:
            st.markdown(
                f"""
                <div style="
                    border: 3px solid white;
                    border-radius: 10px;
                    padding: 10px;
                    background-color: #342b44;
                    color: white;
                    margin-bottom: 5px;
                    margin-top: 20px;
                ">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 5px; margin-bottom: 5px;">
                        <img src="{protocol['image']}" width="50" height="50" style="border-radius: 50%;">
                        <h4 style="margin: 0;color: #FFA500">{protocol['name']}</h4>
                    </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(f"""
                <div style="
                        border: 2px solid white;
                        border-radius: 10px;
                        padding: 20px;
                        background-color: #376a94;
                        color: white;
                        margin-bottom: 5px;
                    ">
                        <div style="margin-top: 20px; font-size: 20x;">
                            <p style="font-size: 20px;">🌐 Site: <a href="{protocol['site']}" style="color: lightblue; font-size: 20px;" target="_blank">Visit Protocol</a></p>
                        </div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown(
        "<hr style='border: 2px double #342b44;'>",
        unsafe_allow_html=True
    )
# --- Footer ---
st.markdown("""
    <style>
        .footer {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;  /* 3 colunas */
            grid-gap: 20px;
            background-color: #342b44;
            color: white;
            padding: 20px;
            font-size: 20px;
        }
        .footer p {
            margin: 0;
        }
        .footer a {
            color: white;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
    <div class="footer">
        <div>
            <p>🪂 Airdrops Monitor</p>
        </div>
        <div style="text-align: center; color: #c9ada7; font-size:20px;">
            Made with ❤️ by <a href="https://x.com/CaioFlemin2089" style="color: white; text-decoration: none;" target="_blank">@CaioFleming</a> |
            Follow for more airdrop farming strategies 🚀<br>
            Stay updated on Twitter and Discord! 📢
            <br>
            <div style="text-align: center; color: #c9ada7; font-size:18px;">
                Disclaimer: This is not financial advice. Always do your own research (DYOR)!
            </div>
        </div>
        <div style="text-align: center; color: #c9ada7; font-size:20px;">
            <p>Community: </p>
            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAAAAABXZoBIAAAA/0lEQVR4AbXPIazCMACE4d+L2qoZFEGSIGcRc/gJJB5XMzGJmK9EN0HMi+qaibkKVF1txdQe4g0YzPK5yyWXHL9TaPNQ89LojH87N1rbJcXkMF4Fk31UMrf34hm14KUeoQxGArALHTMuQD2cAWQfJXOpgTbksGr9ng8qluShJTPhyCdx63POg7rEim95ZyR68I1ggQpnCEGwyPicw6hZtPEGmnhkycqOio1zm6XuFtyw5XDXfGvuau0dXHzJp8pfBPuhIXO9ZK5ILUCdSvLYMpc6ASBtl3EaC97I4KaFaOCaBE9Zn5jUsVqR2vcTJZO1DdbGoZryVp94Ka/mQfE7f2T3df0WBhLDAAAAAElFTkSuQmCC" width="24" height="24" style="border-radius: 50%;">
            <a href="https://twitter.com/" target="_blank">Twitter</a>
            <p><a href="https://discordbot.streamlit.app/" target="_blank">🤖 Discord Bot</a></p>
        </div>
    </div>
""", unsafe_allow_html=True)

#438.153.573.297.839
#12.606.232.983

