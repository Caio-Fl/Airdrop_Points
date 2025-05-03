import streamlit as st
import plotly.express as px
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
from PIL import Image
import webbrowser
import sqlite3
import json

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

# --- Header ---
st.markdown('<div class="header"> Airdrops Monitor </div>', unsafe_allow_html=True)

st.markdown(
    "<hr style='border: 2px double #342b44;'>",
    unsafe_allow_html=True
)

# --- Sidebar ---
st.sidebar.title("Airdrops Menu")
st.sidebar.markdown("<h3 style='font-size: 20px;'></h3>", unsafe_allow_html=True)
opcao = st.sidebar.radio("", ["Farm with YT", "Comparative YT Table", "Latest Airdrops", "Depin Airdrops", "Bridges & Swaps Protocols"])

st.markdown("\n\n")
st.sidebar.markdown("---")
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
            "Link": "<a href='https://app.level.money/farm?referralCode=pwlblh' target='_blank'>More info</a>",
            "Grade": f"{Level_grade}",
            "TVL": f"{Level_tvl} M",
            "Last Update": f"{time_Level}",
            "Expiry": f"{date3}",
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
            "Link": "<a href='https://portal.openeden.com/bills-campaign?refCode=1WgbBka17k' target='_blank'>More info</a>",
            "Grade": f"{Open_grade}",
            "TVL": f"{Open_tvl} M",
            "Last Update": f"{time_Open}",
            "Expiry": f"{date2}",
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
            "Link": "<a href='https://app.fragmetric.xyz/referral?ref=77XL68' target='_blank'>More info</a>",
            "Grade": f"{Frag_grade}",
            "TVL": f"{Frag_tvl} M",
            "Last Update": f"{time_Level}",
            "Expiry": f"{date4}",
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
            "Link": "<a href='https://boost.kyros.fi/?ref=nq3orn' target='_blank'>More info</a>",
            "Grade": f"{Ky_grade}",
            "TVL": f"{Ky_tvl} M",
            "Last Update": f"{time_Level}",
            "Expiry": f"{date5}",
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

# --- Conteúdo Principal ---
st.title(opcao)

if opcao == "Farm with YT":
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
                    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 5px;">
                        <img src="{protocolos[p]['Imagem']}" width="200" height="70" style="border-radius: 5%;">
                        <h4 style="margin: 5;color: #FFA500">{p}</h4>
                    </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(f"""
            <div style="background-color: #376a94; padding: 20px; border: 2px solid white; border-radius: 10px; margin-top: 20px; font-size: 16px;margin-bottom: 5px;">
                <img src="{protocolos[p]['Imagem']}" width="200"><br><br>
                <h2>Detalhes de {p}</h2>
                <p style="font-size:18px;"><strong>Protocol:</strong> {p} – <a href="{protocolos[p]['Link']}" target="_blank">{protocolos[p]['Link']}</a></p>
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

        if st.button("🔙 Voltar"):
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

elif opcao == "Latest Airdrops":
    st.info("🚧 Em breve: Estratégias de looping de YT.")

elif opcao == "Depin Airdrops":
    st.info("🚧 Em breve: Protocolos de Bridges.")

elif opcao == "Comparative YT Table":

    df = pd.DataFrame({
        "Protocolo": protocolos.keys(),
        "TVL": [protocolos[p]["TVL"] for p in protocolos],
        "Expected ROI": [protocolos[p]["Expected ROI"] for p in protocolos],
        "YT-Multiplier": [protocolos[p]["YT Multiplier"] for p in protocolos],
        "Protocol Boost": [protocolos[p]["Boost"] for p in protocolos],
        "Expiry": [protocolos[p]["Expiry"] for p in protocolos],
        "Rating": [protocolos[p]["Rating"] for p in protocolos],
    })
    # Mostrando no Streamlit
    #st.dataframe(df, use_container_width=True)
    styled_df = df.style.applymap(lambda v: 'color: green' if isinstance(v, (int, float)) and v > 0.1 else 'color: #342b44')
    st.write(styled_df)

elif opcao == "Bridges & Swaps Protocols":
    st.info("🚧 Em breve: Protocolos de Bridges.")   

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

