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
from PIL import Image


st.set_page_config(page_title="Painel de Dados Airdrops", layout="wide")
st.title("📈 Monitoring Painel for YT Airdrops Farming")

API_URL = "http://localhost:8000/dados"

# Simulação de armazenamento temporário (poderia ser substituído por banco ou API GET)
if "dados" not in st.session_state:
    st.session_state.dados = []

# Simulando leitura via POST (em produção, ideal via GET ou banco de dados)
def enviar_dados():
    Total_OpenEden = get_leader_OpenEden_function()
    time_Open = datetime.now().now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    Total_Level = get_leader_Level_function()
    time_Level = datetime.now().now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    tags = ["OpenEden","Level"]
    values = [Total_OpenEden,Total_Level]
    dado = {
        "tag": tags[0],
        "value": values[0]
    }
    #try:
    #    resp = requests.post(API_URL, json=dado)
    #    if resp.status_code == 200:
    #        st.session_state.dados = []
    #        st.session_state.dados.append(dado)
            # Atualiza o horário de última atualização
            #st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #except:
    #    st.warning("⚠️ Não foi possível conectar à API.")
    return(tags,values,time_Open,time_Level)

# Botão manual para simular envio
#if st.button("➕ Load Total Points of Protocols"):
i = 0

Open_Data = []
Open_Multipleir = 10
Open_Boost = 1.05
Open_TP_0 = 9851534492
Open_date0 = datetime.strptime("2025-04-09T08:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

Level_Data = []
Level_Multipleir = 40
Level_Boost = 1.10
Level_TP_0 = 117375084663151
Level_date0 = datetime.strptime("2025-03-27T08:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

Frag_Data = []
Frag_Multipleir = 4
Frag_Boost = 1.10
Backpack_Boost = 1.30
Frag_TP_0 = 9710000000
Frag_date0 = datetime.strptime("2025-04-07T08:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

placeholder = st.empty()  # espaço vazio que vamos atualizar no loop
df2 = pd.DataFrame(columns=["time", "value"])
#invested = st.number_input("Value to Invest $:", min_value=0.0, step=0.1)
st.subheader("📋 Insert Data to Calculate the Expected Profit and ROI for Hold YT Tokens")
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

Open_pts_token = 1
Level_pts_token = 2400
Frag_pts_token = 86.4
while True:
    with placeholder.container():
        image = "https://github.com/Caio-Fl/Airdrop_Points/blob/main/banner.png?raw=true"
        st.image(image,use_container_width=True)

        st.subheader("📋 Total Points Farmed by Protocol")


        if i == 0:
            info_box = st.empty()
            info_box.info("Loading Data...")
        else:
            info_box.empty()
      
        tags, values, time_Open, time_Level = enviar_dados()
        Frag_accured,Frag_unApy,solAsUSD,fragAsUSD,fragBySol,total_users = get_fragmetric_data()
        #Open_Data.append([values[0],time_Open])
        #Level_Data.append([values[1],time_Level])
        Open_ytMul,Open_unApy,Open_impApy,Open_feeRate,Open_swapFee,Open_ytRoi,Open_expiry,Open_priceImpact = get_Pendle_Data("0xa77c0de4d26b7c97d1d42abd6733201206122e25","0x42E2BA2bAb73650442F0624297190fAb219BB5d5")
        Level_ytMul,Level_unApy,Level_impApy,Level_feeRate,Level_swapFee,Level_ytRoi,Level_expiry,Level_priceImpact = get_Pendle_Data("0xe45d2ce15abba3c67b9ff1e7a69225c855d3da82","0x65901Ac9EFA7CdAf1Bdb4dbce4c53B151ae8d014")
        Frag_ytMul,Frag_Multiplier,Frag_expiry,Frag_swapFee,Frag_priceImpact,time_Frag = get_rateX_data()

        date_obj = datetime.strptime(time_Open, "%Y-%m-%d %H:%M:%S")
        date_utc_formatada = date_obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        date1 = datetime.strptime(date_utc_formatada , "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        date2 = datetime.strptime(Open_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        date3 = datetime.strptime(Level_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        date4 = datetime.strptime(Frag_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

        Open_date_tge = datetime.strptime((Open_l_date+"T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        Open_mean_daily = 1.3*(values[0]-Open_TP_0)/((date1-Open_date0).days)
        Open_points_tge = round(values[0] + (((Open_date_tge-date1).days)*Open_mean_daily),0)
        Open_points_per_token = round(Open_points_tge/(tsp*drop/100),2)

        Level_date_tge = datetime.strptime((Level_l_date+"T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        Level_mean_daily = 1.3*(values[1]-Level_TP_0)/((date1-Level_date0).days)
        Level_points_tge = round(values[1] + (((Level_date_tge-date1).days)*Level_mean_daily),0)
        Level_points_per_token = round(Level_points_tge/(tsp*drop/100),2)
        
        Frag_date_tge = datetime.strptime((Frag_l_date+"T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        Frag_mean_daily = 1.3*(Frag_accured-Frag_TP_0)/((date1-Frag_date0).days)
        Frag_points_tge = round(Frag_accured + (((Frag_date_tge-date1).days)*Frag_mean_daily),0)
        Frag_points_per_token = round(Frag_points_tge/(tsp*drop/100),2)

        # Mostrar dados recebidos
        #df = pd.DataFrame(st.session_state.dados)
        if values[0] != 0:
            # Adicionar unidade
            #df['Total Points Farmed'] = df['value'].astype(str) + " XP"
            
            st.markdown(f" ")
            st.markdown(f"<p style='font-size:22px;'>🔹 Protocol: {tags[0]}  - {"<a href='https://portal.openeden.com/bills-campaign?refCode=1WgbBka17k' target='_blank'>🔗 More info</a>"}</p>", unsafe_allow_html=True)
            st.markdown(f"  🏆 **Total Points Farmed:** {values[0]} XP ") 
            st.markdown(f"  🕒 **Last Update:** {time_Open}")
            st.markdown(f"  🚀 **Pendle YT-cUSDO:** {round(Open_ytMul,3)}")
            st.markdown(f"  📈 **Pendle YT-cUSDO APY:** {round(Open_unApy*100,2)} %")
            st.markdown(f"  🗓️ **Time Until YT-cUSDO Expiration:** {(date2-date1)}")
            st.markdown(f"  ✖️ **Protocol YT Multiplier:** {Open_Multipleir}")
            st.markdown(f"  💥 **Protocol Referral Boost:** {round((Open_Boost-1),2)*100} %")
            st.markdown(f"  💴 **Equivalent YT-cUSDO Received: $** {round(invested*Open_ytMul,2)}")
            st.markdown(f"  ✨ **Daily Points Farmed:** {round(invested*Open_ytMul*Open_Multipleir*Open_Boost*Open_pts_token,2)} XP")
            st.markdown(f"  🌟 **Total Points Farmed in YT Expiration:** {round(invested*Open_ytMul*Open_Multipleir*Open_Boost*Open_pts_token*(date2-date1).days,2)} XP")
            st.markdown(f"  💵 **Farmed Yield in YT Expiration: $** {round(invested*Open_ytMul*Open_unApy*(date2-date1).days/365,2)}")
            st.markdown(f"  🧮 **Mean Daily Points (x 1.30):** {Open_mean_daily} XP")
            st.markdown(f"   ∑ **Estimated Total Points in TGE:** {Open_points_tge} XP")
            st.markdown(f"  💎 **Points to Receive 1 OpenEden Token:** {Open_points_per_token} XP")
            st.markdown(f"  💲 **Estimated Token Price : $** {fdv/tsp}")
            st.markdown(f"  🪙 **Estimated Tokens Airdrop :** {round((invested*Open_ytMul*Open_Multipleir*Open_Boost*Open_pts_token*(date2-date1).days)/Open_points_per_token,2)}")
            st.markdown(f"  💰 **Estimated Airdrop Value: $** {round((fdv/tsp)*(invested*Open_ytMul*Open_Multipleir*Open_Boost*Open_pts_token*(date2-date1).days)/Open_points_per_token,2)}")
            st.markdown(f"  🤑 **Profit : $** {round((((fdv/tsp)*(invested*Open_ytMul*Open_Multipleir*Open_Boost*Open_pts_token*(date2-date1).days)/Open_points_per_token)+(invested*Open_ytMul*Level_unApy*(date3-date1).days/365)-invested-(invested*Open_priceImpact)),2)}")
            st.markdown(f"  🤞 **ROI :** {round(100*(((fdv/tsp)*(invested*Open_ytMul*Open_Multipleir*Open_Boost*Open_pts_token*(date2-date1).days)/Open_points_per_token)+(invested*Open_ytMul*Open_unApy*(date3-date1).days/365)-invested-(invested*Open_priceImpact))/abs((invested*Open_ytMul*Open_unApy*(date2-date1).days/365)-invested-(invested*Open_priceImpact)),2)} %")
            st.markdown(f" ")
            st.markdown(f"<p style='font-size:22px;'>🔹 Protocol: {tags[1]}  - {"<a href='https://app.level.money/farm?referralCode=pwlblh' target='_blank'>🔗 More info</a>"}</p>", unsafe_allow_html=True)
            st.markdown(f"  🏆 **Total Points Farmed:** {values[1]} XP ") 
            st.markdown(f"  🕒 **Last Update:** {time_Level}")
            st.markdown(f"  🚀 **Pendle YT-lvlUSD:** {round(Level_ytMul,3)}")
            st.markdown(f"  📈 **Pendle YT-lvlUSD APY:** {round(Level_unApy*100,2)} %")
            st.markdown(f"  🗓️ **Time Until YT-lvlUSD Expiration:** {(date3-date1)}")
            st.markdown(f"  ✖️ **Protocol YT Multiplier:** {Level_Multipleir}")
            st.markdown(f"  💥 **Protocol Referral Boost:** {round((Level_Boost-1),2)*100} %")
            st.markdown(f"  💴 **Equivalent YT-lvlUSD Received: $** {round(invested*Level_ytMul,2)}")
            st.markdown(f"  ✨ **Daily Points Farmed:** {round(invested*Level_ytMul*Level_Multipleir*Level_Boost*Level_pts_token,2)} XP")
            st.markdown(f"  🌟 **Total Points Farmed in YT Expiration:** {round(invested*Level_ytMul*Level_Multipleir*Level_Boost*Level_pts_token*(date3-date1).days,2)} XP")
            st.markdown(f"  💵 **Farmed Yield in YT Expiration: $** {round(invested*Level_ytMul*Level_unApy*(date3-date1).days/365,2)}")
            st.markdown(f"  🧮 **Mean Daily Points (x 1.30):** {Level_mean_daily} XP")
            st.markdown(f"   ∑ **Estimated Total Points in TGE:** {Level_points_tge} XP")
            st.markdown(f"  💎 **Points to Receive 1 Level Token:** {Level_points_per_token} XP")
            st.markdown(f"  💲 **Estimated Token Price : $** {fdv/tsp}")
            st.markdown(f"  🪙 **Estimated Tokens Airdrop :** {round((invested*Level_ytMul*Level_Multipleir*Level_Boost*Level_pts_token*(date3-date1).days)/Level_points_per_token,2)}")
            st.markdown(f"  💰 **Estimated Airdrop Value: $** {round((fdv/tsp)*(invested*Level_ytMul*Level_Multipleir*Level_Boost*Level_pts_token*(date3-date1).days)/Level_points_per_token,2)}")            
            st.markdown(f"  🤑 **Profit : $** {round((((fdv/tsp)*(invested*Level_ytMul*Level_Multipleir*Level_Boost*Level_pts_token*(date3-date1).days)/Level_points_per_token)+(invested*Level_ytMul*Level_unApy*(date3-date1).days/365)-invested-(invested*Level_priceImpact)),2)}")
            st.markdown(f"  🤞 **ROI :** {round(100*(((fdv/tsp)*(invested*Level_ytMul*Level_Multipleir*Level_Boost*Level_pts_token*(date3-date1).days)/Level_points_per_token)+(invested*Level_ytMul*Level_unApy*(date3-date1).days/365)-invested-(invested*Level_priceImpact))/abs((invested*Level_ytMul*Level_unApy*(date3-date1).days/365)-invested-(invested*Level_priceImpact)),2)} %")
            st.markdown(f" ")
            st.markdown(f"<p style='font-size:22px;'>🔹 Protocol: Fragmetric  - {"<a href='https://app.fragmetric.xyz/referral?ref=77XL68' target='_blank'>🔗 More info</a>"}</p>", unsafe_allow_html=True)
            st.markdown(f"  🏆 **Total Points Farmed:** {Frag_accured} XP ") 
            st.markdown(f"  🕒 **Last Update:** {time_Level}")
            st.markdown(f"  💱 **fragSOL Price: $** {round((fragAsUSD),2)}")
            st.markdown(f"  ⛃ **Equivalent Invested in fragSOL:** {round((invested/fragAsUSD),3)}")
            st.markdown(f"  🚀 **Rate-X YT-fragSOL:** {round(Frag_ytMul,3)}")
            st.markdown(f"  📈 **Rate-X YT-fragSOL APY:** {round(Frag_unApy*100,2)} %")
            st.markdown(f"  🗓️ **Time Until YT-fragSOL Expiration:** {(date4-date1)}")
            st.markdown(f"  ✖️ **Protocol YT Multiplier:** {Frag_Multipleir}")
            st.markdown(f"  💥 **Protocol Referral Boost:** {round((Frag_Boost-1),2)*100} %")
            st.markdown(f"  💥 **Backpack Boost:** {round((Backpack_Boost-1),2)*100} %")
            st.markdown(f"  💴 **Equivalent YT-fragSOL Received:** {round((invested/fragAsUSD)*Frag_ytMul,2)}")
            st.markdown(f"  ✨ **Daily Points Farmed:** {round((invested/fragAsUSD)*Frag_ytMul*Frag_Multipleir*Frag_Boost*Backpack_Boost*Frag_pts_token,2)} XP")
            st.markdown(f"  🌟 **Total Points Farmed in YT Expiration:** {round((invested/fragAsUSD)*Frag_ytMul*Frag_Multipleir*Frag_Boost*Backpack_Boost*Frag_pts_token*(date4-date1).days,2)} XP")
            st.markdown(f"  💵 **Farmed Yield in YT Expiration:** {round((invested/fragAsUSD)*Frag_ytMul*Frag_unApy*(date4-date1).days/365,2)} fragSOL = $ {round(fragAsUSD*(invested/fragAsUSD)*Frag_ytMul*Frag_unApy*(date4-date1).days/365,2)}")
            st.markdown(f"  🧮 **Mean Daily Points (x 1.30):** {round(Frag_mean_daily,2)} XP")
            st.markdown(f"   ∑ **Estimated Total Points in TGE:** {Frag_points_tge} XP")
            st.markdown(f"  💎 **Points to Receive 1 Fragmetric Token:** {Frag_points_per_token} XP")
            st.markdown(f"  💲 **Estimated Token Price : $** {fdv/tsp}")
            st.markdown(f"  🪙 **Estimated Tokens Airdrop :** {round(((invested/fragAsUSD)*Frag_ytMul*Frag_Multipleir*Frag_Boost*Backpack_Boost*Frag_pts_token*(date4-date1).days)/Frag_points_per_token,2)}")
            st.markdown(f"  💰 **Estimated Airdrop Value: $** {round((fdv/tsp)*((invested/fragAsUSD)*Frag_ytMul*Frag_Multipleir*Frag_Boost*Backpack_Boost*Frag_pts_token*(date4-date1).days)/Frag_points_per_token,2)}")            
            st.markdown(f"  🤑 **Profit : $** {round(((((fdv/tsp)*(invested/fragAsUSD)*Frag_ytMul*Frag_Multipleir*Frag_Boost*Backpack_Boost*Frag_pts_token*(date4-date1).days)/Frag_points_per_token)+((invested)*Frag_ytMul*Frag_unApy*(date4-date1).days/365)-(invested)-((fragAsUSD)*Frag_swapFee)),2)}")
            st.markdown(f"  🤞 **ROI :** {round(100*((((fdv/tsp)*(invested/fragAsUSD)*Frag_ytMul*Frag_Multipleir*Frag_Boost*Backpack_Boost*Frag_pts_token*(date4-date1).days)/Frag_points_per_token)+((invested)*Frag_ytMul*Frag_unApy*(date4-date1).days/365)-(invested)-((fragAsUSD)*Frag_swapFee))/abs(((invested)*Frag_ytMul*Frag_unApy*(date4-date1).days/365)-(invested)-((fragAsUSD)*Frag_swapFee)),2)} %")
            st.markdown(f" ")
            info_box.empty()

        else:
            info_box.info("No data received!")
        i += 1
        
        time.sleep(60)
