import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import time
from datetime import datetime, timezone
from get_leader_OpenEden_function import get_leader_OpenEden_function
from get_leader_Level_function import get_leader_Level_function
from get_Leader_Spark_Data import get_Leader_Spark_Data
from get_fragmetric_data import get_fragmetric_data
from get_Pendle_Data import get_Pendle_Data
from get_rateX_data import get_rateX_data
from get_leader_kyros_function import get_leader_kyros_function
from get_defillama_info import get_defillama_info
from protocol_rate import protocol_rate
from getAllPendleMarkets import get_pendle_apy_data, get_pendle_markets
from barra_compra_venda import barra_compra_venda
import re
from PIL import Image
import requests
import webbrowser
import sqlite3
import json
from streamlit_option_menu import option_menu
import statistics
from mistralai import Mistral
from dotenv import load_dotenv
from mistralai.models import UserMessage
from mistralai.models import File
load_dotenv("apikey.env")  # Load .env file
import os
#from mistralai.client import MistralClient
os.environ["MISTRAL_API_KEY"] = "3DwmTII9fJMoAJRN8XoXf1Wg6aMKg7tu"
api_key = os.getenv("MISTRAL_API_KEY")

#id's = 1 - ETH , 10 OP , 56 - BNB, 146 - SONIC LABS, 5000 - Mantle, 8453 - Base, 42161 - Arb, 80094 -BERA
ids = [1, 56, 146, 5000, 8453, 42161, 80094, 10]
nets = ["Ethereum", "BNB Chain", "Sonic Labs", "Mantle", "Base", "Arbitrum", "Berachain", "Optimism"]

all_markets_list = []

for i, id in enumerate(ids):
    markets = get_pendle_markets(id)
    if not markets.empty:
        net = nets[i]
        markets = markets.copy()
        markets['expiry_date'] = markets["expiry"].str.split('T').str[0]
        markets['net'] = net
        markets["label"] = markets["name"] + " (Expires in: " + markets['expiry_date'] + ") " + net
        all_markets_list.append(markets)

# Concatenar todos os DataFrames em um só
markets = pd.concat(all_markets_list, ignore_index=True)

print(markets[['name', 'expiry_date', 'net', 'label']])
# Exibindo a lista de seleção múltipla
#selected_names = st.multiselect("Escolha um ou mais mercados", options)

# Define o mercado desejado (exatamente como aparece no 'label')
default_market_name = "slvlUSD"  # substitua pela label desejada

# Buscar índice do mercado default
default_index = markets[markets["name"] == default_market_name].index
default_index = int(default_index[0]) if not default_index.empty else 0  # fallback para 0 se não encontrar

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
        index=default_index,
        format_func=lambda x: x.upper()
    )    
    time_scale = st.selectbox(
        "Time in:",
        ["hour", "day"],
        format_func=lambda x: x.upper()
    )

# Pega o mercado selecionado com base no label
selected_row = markets[markets["label"] == selected_label].iloc[0]
net_name = markets.loc[markets["label"] == selected_label, "net"].iloc[0]
print(net_name)
id = ids[nets.index(net_name)]
# Pegando o address
if not selected_row.empty:
    address = selected_row["address"]
    label = selected_row["label"]
    expires = selected_row["expiry"]
    st.markdown(f"<span style='font-size:22px'><strong>Selected Market:</strong> {label}</span>", unsafe_allow_html=True)
else:
    st.markdown("Maket not Founded")

with st.spinner('Loading Pendle Data to Plot Implied APY Tendency...'):
    df_implied,implied_apy,underlying_apy,base_apy,tvl_in_k,trend_line,upper_line,lower_line,trend_line_extended,upper_line_extended,lower_line_extended,dates,extended_dates,expiry_date,address = get_pendle_apy_data(selected_row,time_scale,id)

    # Supondo que base_apy seja uma lista ou Series
    base_apy_series = pd.Series(base_apy)

    # Calcular Q1, Q3 e IQR
    Q1 = base_apy_series.quantile(0.2)
    Q3 = base_apy_series.quantile(0.8)
    IQR = Q3 - Q1

    # Definir limites
    lower_bound = Q1 - 1.2 * IQR
    upper_bound = Q3 + 1.2 * IQR

    # Filtrar dados válidos
    mask = (base_apy_series >= lower_bound) & (base_apy_series <= upper_bound)
    filtered_dates = [d for d, keep in zip(dates, mask) if keep]
    filtered_base_apy = base_apy_series[mask].tolist()
    Range = upper_line[-1] - lower_line[-1]
    trend_perc = 100*(trend_line[-1] - lower_line[-1])/Range
    actual_perc = 100*(implied_apy[-1] - lower_line[-1])/Range
    time_now = datetime.now().now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    data1 = datetime.strptime(time_now, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    delta = expiry_date - data1

            

    # Criar figura
    fig = go.Figure()

    # Base e Implied APY
    fig.add_trace(go.Scatter(x=filtered_dates, y=filtered_base_apy, mode='lines+markers', name='Base APY', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=dates, y=implied_apy, mode='lines+markers', name='Implied APY', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=dates, y=trend_line, mode='lines', name='Implied APY Tendency', line=dict(color='black', dash='dash')))
    fig.add_trace(go.Scatter(x=dates, y=upper_line, mode='lines', name='Maximum Implied APY Tendency', line=dict(color='red', dash='dash')))
    fig.add_trace(go.Scatter(x=dates, y=lower_line, mode='lines', name='Minimum Implied APY Tendency', line=dict(color="#b3a13c", dash='dash')))
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

    def normalizar_para_faixa(valor, min_origem=0, max_origem=100, min_dest=-100, max_dest=100):
        return min_dest + ((valor - min_origem) / (max_origem - min_origem)) * (max_dest - min_dest)

    valor = normalizar_para_faixa(round(actual_perc,2))
    figura = barra_compra_venda(valor,round(actual_perc,2))
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.pyplot(figura)

    def get_token_info(marketAdd,id):
        url = f"https://api-v2.pendle.finance/core/v1/{id}/markets/{marketAdd}"
        response = requests.get(url)
        jsonn = json.loads(response.text)
        #jsonn.get("underlyingApy", {}) 
        ytRoi = jsonn.get("ytRoi", {})
        
        url = f"https://api-v2.pendle.finance/core/v1/sdk/{id}/markets/{marketAdd}/swapping-prices"
        response = requests.get(url)
        jsonn = json.loads(response.text)
        ytMult = jsonn.get("underlyingTokenToYtRate", {})
        return(ytMult,ytRoi)
    print(address)
    ytMult, ytRoi = get_token_info(address,id)
    # IA anwser
    criteria = criteria = """Learn the following Criteria, no mention it you just will use this to awnser the next question: An "Actual Implied APY"  next to "Maximum Historical APY" can be an excellent moment to sell the Yield Token if you already hold the token; An "Actual Implied APY"  next to "Minimum Historical APY" can be an excellent moment to buy the Yield Token; An "Actual Implied APY"  next or higher than "Actual Best Sell point of Implied APY" can be a great moment to sell the Yield Token if you already hold the token if you not holding it ignore; An "Actual Implied APY"  next or a little lower than "Actual Best Buy point of Implied APY" can be a great moment to buy the Yield Token this is an important factor; An "Actual Implied APY"  very lower than "Actual Best Buy point of Implied APY" indicates a possible problem with Yield Token and need to be excluded as an investiment; An "Actual Implied APY percentual in relation of Range" next or higher than 100 indicates na great moment to sell the Yield Tokenif you already hold the token; An "Actual Implied APY percentual in relation of Range" next to 0 or a little negative indicates na great moment to buy the Yield Token; An "Actual Implied APY percentual in relation of Range" very negative indicates a possible problem with Yield Token and need to be excluded as an investiment; If "Days to expiry" is lower than 20, this implies in a high risk to try trade it. An "Actual Underlying APY" higher than 9 is an excellent yield return for hold the YT token, but is necessary to evaluate the days until expiry. An "Actual Underlying APY" lower than 4 is not so good yield return for hold the YT token, but is necessary to evaluate the days until expiry. An "Actual Underlying APY" equals to 0 implies that the yield token do not have any yield return and is just used to farm points. The YT multiplier factor indicates the multiplication factor over the invested capital and the underlying APY gives the yield return based in (YT Multiplier x Invested Capital x Actual Underlying APY/100 x Days to expiry/365), so higher YT miltiplier means that you can receire more yield and farm with higher capital the protocol of token, but if underlying APY is zero you will just farm points in protocol airdrop. YT ROI for hold token up to expiry is the return at maturity o YT token, higher YT ROI means a smaller loss at maturity.
    """
    description = f"""
    Implied APY Data of {label}:
    Actual Implied APY = {round(implied_apy[-1],2)}
    Maximum Historical APY = {round(max(implied_apy),2)}
    Minimum Historical APY = {round(min(implied_apy),2)}
    Actual Best Sell point of Implied APY = {round(upper_line[-1],2)}
    Actual Mean Implied APY = {round(trend_line[-1],2)}
    Actual Best Buy point of Implied APY = {round(lower_line[-1],2)}
    Mean Implied APY percentual in relation of Range = {round(trend_perc,2)}
    Actual Implied APY percentual in relation of Range = {round(actual_perc,2)}
    Time to expiry and YT value goes to zero = {expiry_date}
    Days to expiry = {delta}
    Actual Underlying APY =  {round(underlying_apy[-1],2)}
    Mean Underlying APY = {round(statistics.mean(underlying_apy),2)}
    Maximum Underlying APY Historical = {round(max(underlying_apy),2)}
    Minimum Underlying APY Historical = {round(min(underlying_apy),2)}
    YT Protocol Multiplir = {ytMult}
    YT ROI for hold token up to expiry = {ytRoi*100} %
    """
    question_1 = f"""faced with two possible scenarios (answer in few lines):
        1st If I already have the YT token and I want to know if it is a good time to sell it?
        2nd If I don't have the YT token and I want to know if it is a good time to buy it or if I should wait for a better opportunity?
        3nd If i want to farm point to airdrop of YT token protocol the YT Protocol Multiplier High and the YT ROI is higher than -35 percent?
        According to the data description: {description}"""
    h = implied_apy#[(len(implied_apy)-50):-1]
    question_2 = f"""
        Verify the historical of implied APY and analysis if is this a good momment to Buy the YT to trade it or not. Also consider {delta} to expiry is of high risk?
        Historical Implied APY = {[round(x, 2) for x in h]}
        the Underlying APY is {round(underlying_apy[-1],2)}
    """
    questions = [criteria, question_1, question_2]
    #AIzaSyC4C4bMviJpBIuR7XXCqqPF81JrrYitlro - gemini

    language = "ingles"
    model = "mistral-large-latest"
    personality = "You are an finantial advisor evaluationg historical data"
    resposta= ""
    time.sleep(3)
    IA_1 = mistral_AI(question_1,language,model,personality)
    IA_1 = IA_1['content']
    time.sleep(3)
    IA_2 = mistral_AI(question_2,language,model,personality)
    IA_2 = IA_2['content']
    IA = [IA_1, IA_2]
    #IA = lang_IA(questions,criteria)


    

    if isinstance(IA, list):
        st.markdown(
            "<h2 style='font-size:24px; color:#333;'>🧠 AI Interpretation:</h2>",
            unsafe_allow_html=True
        )
        for resposta in IA:
            st.markdown(
                f"<div style='padding: 15px; border-radius: 10px; background-color: #342b44; font-size: 18px;'>{resposta}</div>",
                unsafe_allow_html=True
            )
            
    else:
        st.markdown(IA)

st.markdown("---")  # Linha separadora entre blocos

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
    <li><strong>Base APY</strong>: This reflects the base yield from the underlying protocol, excluding any incentive rewards.</li>
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
