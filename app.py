import streamlit as st
import plotly.express as px
import requests
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

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Painel de Dados Airdrops", page_icon="🇾🇹", layout="wide")

page_bg_img = '''
<style>
body {
background-image: url("https://i.postimg.cc/xjRJQvgy/stars-3750824-1920.png");
background-size: cover;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

# Banner no topo
image = "https://github.com/Caio-Fl/Airdrop_Points/blob/main/banner.png?raw=true"
st.image(image,use_container_width=True)

# Título
st.title("Monitoring Painel for YT Airdrops Farming")


st.markdown(
    "<p style='font-size:20px;'>&nbsp;&nbsp;&nbsp;Contribute to more content like this, Follow on 𝕏 <a href='https://x.com/CaioFlemin2089'>@CaioFleming</a></p>",
    unsafe_allow_html=True
)

API_URL = "http://localhost:8000/dados"


# Simulação de armazenamento temporário (poderia ser substituído por banco ou API GET)
if "dados" not in st.session_state:
    st.session_state.dados = []


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


# Criar as Variáveis inseridas pelo usuário no Dashboard Streamlit

with st.sidebar:
    st.header("YT Airdrop Farming")
    st.subheader("📋 Insert Data to Calculate ROI")
    invested = st.number_input(
        "Choose the Value to Invest: $",
        min_value=0,
        max_value=100000000,
        value=1000,   # valor padrão
        step=1
    )

    tsp = st.number_input(
        "Expected Token Total Supply:",
        min_value=0,
        max_value=1000000000000,
        value=1000000000,   # valor padrão
        step=1
    )

    drop = st.number_input(
        "Expected Percentual to Protocol Airdrop:",
        min_value=0,
        max_value=100,
        value=5,   # valor padrão
        step=1
    )

    fdv = st.number_input(
        "Expected FDV in TGE: $",
        min_value=0,
        max_value=100000000000,
        value=200000000,   # valor padrão
        step=1
    )

    Open_l_date = st.text_input(
        "Expected OpenEden TGE Date:",
        value="2025-09-30",   # valor padrão
    )

    Level_l_date = st.text_input(
        "Expected Level TGE Date:",
        value="2025-08-08",   # valor padrão
    )

    Frag_l_date = st.text_input(
        "Expected Fragmetric TGE Date:",
        value="2025-09-30",   # valor padrão
    )

    Ky_l_date = st.text_input(
        "Expected Kyros TGE Date:",
        value="2025-07-30",   # valor padrão
    )
st.markdown("---")
st.subheader("📋 Total Points Farmed by Protocol")
# Loop de calculos dos parâmetros que serão mostrados ao usuário no dashboard da Streamlit
placeholder = st.empty()  # espaço vazio que vamos atualizar no loop
while True:
    with placeholder.container():
        # Intro Dashboard

        with st.spinner('Loading Data and Calculating Parameters...'):
            try: 
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

                # Formata a data atual e as datas de TGE (informadas pelo usuário) para que possam ser subtraídas
                date_obj = datetime.strptime(time_Open, "%Y-%m-%d %H:%M:%S")
                date_utc_formatada = date_obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                date1 = datetime.strptime(date_utc_formatada , "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                date2 = datetime.strptime(Open_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                date3 = datetime.strptime(Level_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                date4 = datetime.strptime(Frag_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                date5 = datetime.strptime(ky_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

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

                # Mostrar dados recebidos no Dashboard
                
                if values[0] != 0:  
                    # Criar 3 colunas lado a lado
                    col1, col2, col3, col4 = st.columns(4) 
                    with col1:        
                        st.markdown(f"<p style='font-size:22px;'>Protocol: {tags[0]}  - {"<a href='https://portal.openeden.com/bills-campaign?refCode=1WgbBka17k' target='_blank'>🔗 More info</a>"} - {"<a href='https://app.pendle.finance/trade/points?chains=ethereum' target='_blank'>🔗 Pendle </a>"}</p>", unsafe_allow_html=True)
                        st.markdown(f"  ⭐ **Grade:** {Open_grade}")
                        st.markdown(f"  🏛️ **TVL: $** {Open_tvl} M ")
                        st.markdown(f"  🏆 **Total Points Farmed:** {round(values[0],0)} XP ") 
                        st.markdown(f"  🕒 **Last Update:** {time_Open}")
                        st.markdown(f"  🚀 **Pendle YT-cUSDO Multiplier:** {round(Open_ytMul,3)}")
                        st.markdown(f"  📈 **Pendle YT-cUSDO APY:** {round(Open_unApy*100,2)} %")
                        st.markdown(f"  🗓️ **Time Until YT-cUSDO Expiration:** {(date2-date1)}")
                        st.markdown(f"  ✖️ **Protocol YT Multiplier:** {Open_Multipleir}")
                        st.markdown(f"  💥 **Protocol Referral Boost:** {round((Open_Boost-1),2)*100} %")
                        st.markdown(f"  💴 **Equivalent YT-cUSDO Received: $** {round(invested*Open_ytMul,2)}")
                        st.markdown(f"  ✨ **Daily Points Farmed:** {Open_daily_pts_farmed} XP")
                        st.markdown(f"  🌟 **Total Points Farmed in YT Expiration:** {Open_total_pts_farmed} XP")
                        st.markdown(f"  👥 **Total Users:** {total_users[0]}")
                        st.markdown(f"  🐋 **Top 100 Points Percentual Concentration:** {round(100*top100[0],2)} %")
                        st.markdown(f"  💵 **Farmed Yield in YT Expiration: $** {Open_farmed_yield}")
                        st.markdown(f"  🧮 **Mean Daily Points (x 1.30):** {Open_mean_daily} XP")
                        st.markdown(f"&nbsp;∑ **Estimated Total Points in TGE:** {Open_points_tge} XP")
                        st.markdown(f"  💎 **Points to Receive 1 OpenEden Token:** {Open_points_per_token} XP")
                        st.markdown(f"  💲 **Estimated Token Price : $** {fdv/tsp}")
                        st.markdown(f"  🪙 **Estimated Tokens Airdrop :** {Open_etimated_tokens}")
                        st.markdown(f"  💰 **Estimated Airdrop Value: $** {Open_airdrop_value}")
                        st.markdown(f"  🤑 **Profit : $** {Open_profit}")
                        st.markdown(f"  🤞 **ROI :** {Open_ROI} %")
                        
                        st.sidebar.markdown("\n")

                    with col2: 
                        st.markdown(f"<p style='font-size:22px;'>Protocol: {tags[1]}  - {"<a href='https://app.level.money/farm?referralCode=pwlblh' target='_blank'>🔗 More info</a>"} - {"<a href='https://app.pendle.finance/trade/points?chains=ethereum' target='_blank'>🔗 Pendle </a>"}</p>", unsafe_allow_html=True)
                        st.markdown(f"  ⭐ **Grade:** {Level_grade}")
                        st.markdown(f"  🏛️ **TVL: $** {Level_tvl} M ")
                        st.markdown(f"  🏆 **Total Points Farmed:** {round(values[1],0)} XP ") 
                        st.markdown(f"  🕒 **Last Update:** {time_Level}")
                        st.markdown(f"  🚀 **Pendle YT-lvlUSD Multiplier:** {round(Level_ytMul,3)}")
                        st.markdown(f"  📈 **Pendle YT-lvlUSD APY:** {round(Level_unApy*100,2)} %")
                        st.markdown(f"  🗓️ **Time Until YT-lvlUSD Expiration:** {(date3-date1)}")
                        st.markdown(f"  ✖️ **Protocol YT Multiplier:** {Level_Multipleir}")
                        st.markdown(f"  💥 **Protocol Referral Boost:** {round((Level_Boost-1),2)*100} %")
                        st.markdown(f"  💴 **Equivalent YT-lvlUSD Received: $** {round(invested*Level_ytMul,2)}")
                        st.markdown(f"  ✨ **Daily Points Farmed:** {Level_daily_pts_farmed } XP")
                        st.markdown(f"  🌟 **Total Points Farmed in YT Expiration:** {Level_total_pts_farmed} XP")
                        st.markdown(f"  👥 **Total Users:** {total_users[1]}")
                        st.markdown(f"  🐋 **Top 100 Points Percentual Concentration:** {round(100*top100[1],2)} %")
                        st.markdown(f"  💵 **Farmed Yield in YT Expiration: $** {Level_farmed_yield}")
                        st.markdown(f"  🧮 **Mean Daily Points (x 1.30):** {Level_mean_daily} XP")
                        st.markdown(f"&nbsp;∑ **Estimated Total Points in TGE:** {Level_points_tge} XP")
                        st.markdown(f"  💎 **Points to Receive 1 Level Token:** {Level_points_per_token} XP")
                        st.markdown(f"  💲 **Estimated Token Price : $** {fdv/tsp}")
                        st.markdown(f"  🪙 **Estimated Tokens Airdrop :** {Level_etimated_tokens}")
                        st.markdown(f"  💰 **Estimated Airdrop Value: $** {Level_airdrop_value}")            
                        st.markdown(f"  🤑 **Profit : $** {Level_profit}")
                        st.markdown(f"  🤞 **ROI :** {Level_ROI} %")
                        
                        st.sidebar.markdown("\n")

                    with col3: 
                        st.markdown(f"<p style='font-size:22px;'>Protocol: Fragmetric  - {"<a href='https://app.fragmetric.xyz/referral?ref=77XL68' target='_blank'>🔗 More info</a>"} - {"<a href='https://app.rate-x.io/referral?ref=H9GnKZON' target='_blank'>🔗 Rate-X </a>"}</p>", unsafe_allow_html=True)
                        st.markdown(f"  ⭐ **Grade:** {Frag_grade}")
                        st.markdown(f"  🏛️ **TVL: $** {Frag_tvl} M ")
                        st.markdown(f"  🏆 **Total Points Farmed:** {round(Frag_accured,0)} XP ") 
                        st.markdown(f"  🕒 **Last Update:** {time_Level}")
                        st.markdown(f"  💱 **{symbol_frag} Price: $** {round((fragAsUSD),2)}")
                        st.markdown(f"  ⛃ **Equivalent Invested in fragSOL:** {round((invested/fragAsUSD),3)}")
                        st.markdown(f"  🚀 **Rate-X YT-fragSOL Multiplier:** {round(Frag_ytMul,3)}")
                        st.markdown(f"  📈 **Rate-X YT-fragSOL APY:** {round(Frag_unApy*100,2)} %")
                        st.markdown(f"  🗓️ **Time Until YT-fragSOL Expiration:** {(date4-date1)}")
                        st.markdown(f"  ✖️ **Protocol YT Multiplier:** {Frag_Multipleir}")
                        st.markdown(f"  💥 **Protocol Referral Boost:** {round((Frag_Boost-1),2)*100} %")
                        st.markdown(f"  💥 **Backpack Boost:** {round((Backpack_Boost-1),2)*100} %")
                        st.markdown(f"  💴 **Equivalent YT-fragSOL Received:** {round((invested/fragAsUSD)*Frag_ytMul,2)}")
                        st.markdown(f"  ✨ **Daily Points Farmed:** {Frag_daily_pts_farmed } XP")
                        st.markdown(f"  🌟 **Total Points Farmed in YT Expiration:** {Frag_total_pts_farmed} XP")
                        st.markdown(f"  👥 **Total Users:** {Frag_total_users}")
                        st.markdown(f"  💵 **Farmed Yield in YT Expiration:** {Frag_farmed_yield} fragSOL = $ {round(fragAsUSD*Frag_farmed_yield,2)}")
                        st.markdown(f"  🧮 **Mean Daily Points (x 1.30):** {round(Frag_mean_daily,2)} XP")
                        st.markdown(f"&nbsp;∑ **Estimated Total Points in TGE:** {Frag_points_tge} XP")
                        st.markdown(f"  💎 **Points to Receive 1 Fragmetric Token:** {Frag_points_per_token} XP")
                        st.markdown(f"  💲 **Estimated Token Price : $** {fdv/tsp}")
                        st.markdown(f"  🪙 **Estimated Tokens Airdrop :** {Frag_etimated_tokens}")
                        st.markdown(f"  💰 **Estimated Airdrop Value: $** {Frag_airdrop_value}")            
                        st.markdown(f"  🤑 **Profit : $** {Frag_profit}")
                        st.markdown(f"  🤞 **ROI :** {Frag_ROI} %")
                        
                        st.sidebar.markdown("\n")

                    with col4: 
                        st.markdown(f"<p style='font-size:22px;'>Protocol: Kyros  - {"<a href='https://boost.kyros.fi/?ref=nq3orn' target='_blank'>🔗 More info</a>"} - {"<a href='https://app.rate-x.io/referral?ref=H9GnKZON' target='_blank'>🔗 Rate-X </a>"}</p>", unsafe_allow_html=True)
                        st.markdown(f"  ⭐ **Grade:** {Ky_grade}")
                        st.markdown(f"  🏛️ **TVL: $** {Ky_tvl} M ")
                        st.markdown(f"  🏆 **Total Points Farmed:** {round(Ky_accured,0)} XP ") 
                        st.markdown(f"  🕒 **Last Update:** {time_Level}")
                        st.markdown(f"  💱 **{symbol_ky} Price: $** {round((KyAsUSD),2)}")
                        st.markdown(f"  ⛃ **Equivalent Invested in kySOL:** {round((invested/KyAsUSD),3)}")
                        st.markdown(f"  🚀 **Rate-X YT-kySOL Multiplier:** {round(ky_ytMul,3)}")
                        st.markdown(f"  📈 **Rate-X YT-kySOL APY:** {round(Ky_unApy*100,2)} %")
                        st.markdown(f"  🗓️ **Time Until YT-kySOL Expiration:** {(date5-date1)}")
                        st.markdown(f"  ✖️ **Protocol YT Multiplier:** {Ky_Multipleir}")
                        st.markdown(f"  💥 **Protocol Referral Boost:** {round((Ky_Boost-1),2)*100} %")
                        st.markdown(f"  💴 **Equivalent YT-kySOL Received:** {round((invested/KyAsUSD)*ky_ytMul,2)}")
                        st.markdown(f"  ✨ **Daily Points Farmed:** {Ky_daily_pts_farmed } XP")
                        st.markdown(f"  🌟 **Total Points Farmed in YT Expiration:** {Ky_total_pts_farmed} XP")
                        st.markdown(f"  👥 **Total Users:** {Ky_total_users}")
                        st.markdown(f"  🐋 **Top 100 Points Percentual Concentration:** {round(100*Ky_top100p,2)} %")
                        st.markdown(f"  💵 **Farmed Yield in YT Expiration:** {Ky_farmed_yield} KySOL = $ {round(KyAsUSD*Ky_farmed_yield,2)}")
                        st.markdown(f"  🧮 **Mean Daily Points (x 1.30):** {round(Ky_mean_daily,2)} XP")
                        st.markdown(f"&nbsp;∑ **Estimated Total Points in TGE:** {Ky_points_tge} XP")
                        st.markdown(f"  💎 **Points to Receive 1 Kyros Token:** {Ky_points_per_token} XP")
                        st.markdown(f"  💲 **Estimated Token Price : $** {fdv/tsp}")
                        st.markdown(f"  🪙 **Estimated Tokens Airdrop :** {Ky_etimated_tokens}")
                        st.markdown(f"  💰 **Estimated Airdrop Value: $** {Ky_airdrop_value}")            
                        st.markdown(f"  🤑 **Profit : $** {Ky_profit}")
                        st.markdown(f"  🤞 **ROI :** {Ky_ROI} %")

                        st.sidebar.markdown("\n")

            except:
                st.success("Error in Loading Data. Please verify if there is connections problem with Protocols API.")    
                
            st.markdown("---")

        i += 1

        # --- Footer ---
        st.markdown("""
            <hr style="margin-top:50px; margin-bottom:20px; border:1px solid #333; font-size:22px;">
            <div style="text-align: center; color: gray; font-size:16px;">
                Made with ❤️ by <a href="https://x.com/CaioFlemin2089" style="color: white; text-decoration: none;" target="_blank">@CaioFleming</a> |
                Follow for more airdrop farming strategies 🚀<br>
                Stay updated on Twitter and Discord! 📢
            </div>
            <br>
            <div style="text-align: center; color: #666; font-size:18px;">
                Disclaimer: This is not financial advice. Always do your own research (DYOR)!
            </div>
        """, unsafe_allow_html=True)

        
        time.sleep(60)
