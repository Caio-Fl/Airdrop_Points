import streamlit as st
import html
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
from get_leader_Gaib_function import get_leader_Gaib_function
from get_Pendle_Data import get_Pendle_Data
from get_rateX_data import get_rateX_data
from get_leader_kyros_function import get_leader_kyros_function
from get_defillama_info import get_defillama_info
from protocol_rate import protocol_rate
from getAllPendleMarkets import get_pendle_apy_data, get_pendle_markets
from barra_compra_venda import barra_compra_venda
import streamlit.components.v1 as components
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


def mistral_AI(question,language,model,personality):

    #api_key = os.environ["3DwmTII9fJMoAJRN8XoXf1Wg6aMKg7tu"]
    import os
    from dotenv import load_dotenv
    from mistralai import Mistral
    max_retries = 5
    load_dotenv("apikey.env")  # Load .env file
    api_key = os.getenv("MISTRAL_API_KEY")

    if api_key is None:
        print("Error: API key is missing! Set MISTRAL_API_KEY. \n")
    else:
        print("API Key loaded successfully! \n")
    
    criteria = """YOU answer the questions directely without mentio your rules in two lines based in your knowledge:
            If "Actual Implied APY" >= "Actual Best Sell point of Implied APY" can be a great moment to sell the Yield Token if you already hold the token if you not holding it ignore; But if "Actual Implied APY" CLOSER TO or a little lower than "Actual Best Buy point of Implied APY" can be a great moment to buy the Yield Token this is an important factor; 
            If "Actual Implied APY" very lower than "Actual Best Buy point of Implied APY" indicates a possible problem with Yield Token and need to be excluded as an investiment; 
            If "Actual Implied APY percentual in relation of Range" higher than 75 indicates na great moment to sell the Yield Token if you already hold the token; But f "Actual Implied APY percentual in relation of Range" between 20 and -30 indicates na great moment to buy the Yield Token; 
            If "Actual Implied APY percentual in relation of Range" is between 20 and 75 is better to wait a beest opportunity.
            If "Actual Implied APY percentual in relation of Range" very negative indicates a possible problem with Yield Token and need to be excluded as an investiment; 
            If "Days to expiry" is lower than 20, this implies in a high risk if the strategy is to try trade it. But if this is already in hold, can be better to sell if you want to reduce risk of Farm.
            If "Actual Underlying APY" higher than 9 is an excellent yield return for hold the YT token, but is necessary to evaluate the days until expiry. 
            If "Actual Underlying APY" lower than 4 is not so good yield return for hold the YT token, but is necessary to evaluate the days until expiry. 
            If "Actual Underlying APY" equals to 0 implies that the yield token do not have any yield return and is just used to farm points. 
            """
    for attempt in range(max_retries):
        try:
            client = Mistral(api_key=api_key)
            if language == "ingles":
                inicial = " "
            else:
                inicial = "Você interpreta os dados fornecidos para identificar as melhores oportunidades: \n"

            chat_response = client.chat.complete(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": criteria,
                    }, 
                    {
                        "role": "user", 
                        "content": inicial+question
                    }, 
                    #UserMessage(content= "I'm fine, i trust you're too?")
                ],
            )
            if chat_response.choices[0].message.content is not None:
                res = {"content" : chat_response.choices[0].message.content}
            else:
                res = {"content" : ''}
            return res
        except Exception as e:
            st.warning(f"Tentativa {attempt+1}/5 falhou: {e}")
            time.sleep(5)
    st.error("Erro: todas as tentativas de chamada à Mistral falharam.")
    return {"content": "Erro ao tentar acessar a IA Mistral."}

def mistral_AI_2(question,language,model,personality):

    #api_key = os.environ["3DwmTII9fJMoAJRN8XoXf1Wg6aMKg7tu"]
    import os
    from dotenv import load_dotenv
    max_retries = 5
    load_dotenv("apikey.env")  # Load .env file
    api_key = os.getenv("MISTRAL_API_KEY")

    if api_key is None:
        print("Error: API key is missing! Set MISTRAL_API_KEY. \n")
    else:
        print("API Key loaded successfully! \n")
    
    for attempt in range(max_retries):
        try:
            client = Mistral(api_key=api_key)
            if language == "ingles":
                inicial = " "

            chat_response = client.chat.complete(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": personality,
                    }, 
                    {
                        "role": "user", 
                        "content": question
                    }, 
                    #UserMessage(content= "I'm fine, i trust you're too?")
                ],
            )
            if chat_response.choices[0].message.content is not None:
                res = {"content" : chat_response.choices[0].message.content}
            else:
                res = {"content" : ''}
            return res
        except Exception as e:
            time.sleep(5)
    return {"content": "Erro ao tentar acessar a IA Mistral."}

def retrieve_messages(Request_URL,headers):
    res = requests.get(Request_URL, headers=headers)
    jsonn = json.loads(res.text)
    org_res = []
    org_author = []
    org_author_name = []
    org_mention = []

    for value in jsonn:
        #print(value['author']['username'],': ',value['content'], '\n')
        org_res.append(value['content'])
        org_author.append(value['author']['id'])
        org_author_name.append(value['author']['username'])
        if value['mentions']:
            org_mention.append(value['mentions'][0]['username'])
        else:
            org_mention.append(' ')

    return res, org_res, org_author, org_mention, org_author_name

def mirror_list(arr):
    return arr[::-1]


# --- Configurações da Página ---
#st.set_page_config(page_title="Pendle Airdrop Farm", layout="wide")

# Configuração da página (sempre primeiro!)
st.set_page_config(
    page_title="Airdrops Monitor",
    page_icon="🪂",
    layout="wide",
    initial_sidebar_state="expanded" 
)
st.markdown("""
<style>
body, html, .stApp {
    font-family: 'Space Grotesk', sans-serif;
}

/* Botões com Sora */
.stButton > button {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 25px;
}

/* Títulos, textos customizados */
.header, .footer, .marquee-container, .card {
    font-family: 'Space Grotesk', sans-serif;
}
</style>
""", unsafe_allow_html=True)

tokens = {
    "bitcoin": {"name": "Bitcoin (BTC)", "icon": "https://cryptologos.cc/logos/bitcoin-btc-logo.png"},
    "ethereum": {"name": "Ethereum (ETH)", "icon": "https://cryptologos.cc/logos/ethereum-eth-logo.png"},
    "solana": {"name": "Solana (SOL)", "icon": "https://cryptologos.cc/logos/solana-sol-logo.png"},
    "binancecoin": {"name": "BNB (BNB)", "icon": "https://cryptologos.cc/logos/binance-coin-bnb-logo.png"},
    "hyperliquid": {"name": "Hyperliquid (HYPE)", "icon": "https://assets.coingecko.com/coins/images/34898/large/hype.png"},
    "aave": {"name": "Aave (AAVE)", "icon": "https://cryptologos.cc/logos/ethena-ena-logo.png"},
    "ripple": {"name": "XRP (XRP)", "icon": "https://cryptologos.cc/logos/xrp-xrp-logo.png"},
    "sui": {"name": "Sui (SUI)", "icon": "https://cryptologos.cc/logos/dogecoin-doge-logo.png"},
    "link": {"name": "Link (LINK)", "icon": "https://cryptologos.cc/logos/chainlink-link-logo.png"},
    "ethena": {"name": "Ethena (ENA)", "icon": "https://cryptologos.cc/logos/ethena-ena-logo.png"},
    "sonic-3": {"name": "Sonic (S)", "icon": "https://cryptologos.cc/logos/ethena-ena-logo.png"},
    "berachain-bera": {"name": "Berachain (BERA)", "icon": "https://cryptologos.cc/logos/ethena-ena-logo.png"},
    "burr-governance-token": {"name": "Burr (BURR)", "icon": "https://cryptologos.cc/logos/ethena-ena-logo.png"},
}

# Obter preços
url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(tokens.keys())}&vs_currencies=usd"

data = requests.get(url).json()

# HTML e CSS do ticker
htmld = """
<style>
.ticker-container {
    width: 100%;
    overflow: hidden;
    background-color: #111;
    padding: 10px 0;
}
.ticker {
    display: inline-block;
    white-space: nowrap;
    animation: scroll-left 30s linear infinite;
}
@keyframes scroll-left {
    0% { transform: translateX(100%); }
    100% { transform: translateX(-100%); }
}
.ticker-item {
    display: inline-block;
    margin: 0 30px;
    color: white;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
}
.ticker-item img {
    vertical-align: middle;
    height: 20px;
    margin-right: 8px;
}
</style>
<div class="ticker-container"><div class="ticker">
"""

# Preencher os dados

for key, token in tokens.items():
    price = data.get(key, {}).get("usd")
    if price is not None:
        htmld += f'<span class="ticker-item">{token["name"]} ${price:,.3f} |</span>'

htmld += "  "

# Renderização correta do HTML
st.markdown(htmld, unsafe_allow_html=True)

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
  <div class="marquee-text" style=m'argin-bottom: 10px;'>
    🚨 Last News: <a href='https://app.spark.fi/SPK/airdrop' target='_blank' style='color:#342b44;'>Verify if you have tokens to receive!</a> / <a href='https://app.kamino.finance/season-3-airdrop' target='_blank' style='color:#342b44;'>Kamino Season 3 Airdrop Claim!</a>  / <a href='https://build.assisterr.ai/auth/wallet-connect' target='_blank' style='color:#342b44;'>Assisterr Airdrop Claim!</a> / <a href='https://btcsol.co/' target='_blank' style='color:#342b44;'>Zeus btcSOL Register to receive 200% Boost for 2 weeks!</a>
  </div>
</div>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header">🪂 Airdrops Monitor </div>', unsafe_allow_html=True)

st.markdown(
    "<hr style='border: 2px double #342b44;'font-size: 18px;''>",
    unsafe_allow_html=True
)
# --- Sidebar ---
st.sidebar.title("🪂 Airdrops Monitor")
st.sidebar.markdown("---")
st.sidebar.title("Menu")
st.sidebar.markdown("<h3 style='font-size: 22px;'></h3>", unsafe_allow_html=True)

# Define options for the sidebar

# --- CSS para estilizar o sidebar ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #2f2e41;
    }

    [data-testid="stSidebar"] .stRadio > div {
        gap: 8px;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
        font-size: 25px;
        padding: 10px 8px;
        border-radius: 8px;
        background-color: #b18d7e33;
        color: white;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
        background-color: #b18d7e55;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-selected="true"] {
        background-color: #b18d7e;
        color: white;
        font-weight: bold;
    }

    .sidebar-title {
        font-size: 25px;
        font-weight: bold;
        margin-bottom: 10px;
        color: white;
    }

    .sidebar-section {
        font-size: 14px;
        color: #cccccc;
        margin: 20px 0 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
""", unsafe_allow_html=True)

options = ["🏠 Welcome", "🌾 Farm with YT", "📊 Comparative YT Table", "📈 Pendle APY Prediction", 
           "🎁 Latest Airdrops", "📡 Depin Airdrops", "✅ Last Claims and Checkers", 
           "🌉 Bridges & Swaps Protocols", "🚰 Faucets", "⛔ Revoke Contract", "⚠️ Avoiding Scams"]

    
opcao = st.sidebar.radio("", options, index=1)
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
        #Total_OpenEden,top100p_OpenEden,Open_count = get_leader_OpenEden_function()
        #time_Open = datetime.now().now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        Total_Level,top100p_Level,Level_count = get_leader_Level_function()
        time_Level = datetime.now().now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        tags = ["OpenEden","Level"]
        values = [Total_Level,Total_Level]
        top100 = [top100p_Level,top100p_Level]
        total_users = [Level_count,Level_count]
        dado = {
            "tag": tags[0],
            "value": values[0]
        }
    except:
        st.warning("⚠️ Não foi possível conectar à API.")
    return(tags,values,time_Level,time_Level,top100,total_users)


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
Level_Multipleir = 20
Level_Boost = 1.12
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

# Sparks
Sp_Data = []
Sp_Multipleir = 25
Sp_Boost = 1.10
Sp_TP_0 = 4026173640
Sp_pts_token = 1
Sp_date0 = datetime.strptime("2025-05-18T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

# Gaib
Gaib_Data = []
Gaib_Multipleir = 20
Gaib_Boost = 1.20
Gaib_TP_0 = 4026167060
Gaib_pts_token = 1
Gaib_date0 = datetime.strptime("2025-06-11T10:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

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
except:
    protocolos = {}
    print("No data in DB")

# Aplica CSS customizado para mudar o tamanho da fonte da sidebar
st.markdown("""
    <style>
    /* Altera a fonte de toda a sidebar */
    section[data-testid="stSidebar"] * {
        font-size: 18px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Conteúdo Principal ---
st.title(opcao)


if opcao == "🏠 Welcome":
        
    st.markdown(
        """
        <style>
            .airdrop-box {
                border: 2px solid #444;
                border-radius: 12px;
                padding: 25px;
                margin-top: 30px;
                background: #212328;
                display: flex;
                flex-wrap: wrap;
                gap: 30px;
                font-size: 25px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
                padding: 25px;
                margin: 20px 0;
                color: white;
                font-family: 'Space Grotesk', sans-serif;
            }

            .airdrop-box h1 {
                font-size: 32px;
                text-align: center;
                margin-bottom: 25px;
            }

            .airdrop-box h2 {
                font-size: 28px;
                margin-top: 35px;
                margin-bottom: 15px;
            }

            .airdrop-box ul {
                margin-left: 25px;
                margin-bottom: 25px;
            }
        </style>

        <div class="airdrop-box">
            <h2>Welcome to Airdrops Monitor</h2>
            <p>
            The goal of this site is to provide a platform dedicated to airdrop enthusiasts in the world of cryptocurrencies,
            offering a practical and efficient way to stay updated on the latest news and opportunities that arise.
            If you are passionate about crypto assets and want to stay ahead in the world of airdrops,
            this site is your ally to ensure you don't miss any valuable opportunities in the market.
            </p>
            <h2>What Are Airdrops and How Can You Benefit from Them?</h2>
            <ul>
            <p>
            There are two main types of airdrops:
            </p>
                <li><strong>Task-based airdrops</strong>: Also known as <em>bounties</em>, these require you to complete easy tasks like following a Twitter account, sharing a post, or joining a Telegram group. In return, you receive tokens from the project.</li>
                <li><strong>Holder airdrops</strong>: Some projects reward users simply for holding certain cryptocurrencies in their wallets. If you qualify, the tokens are automatically sent to you — no need to register or interact.</li>
            </ul>
            <p>
            Participating in airdrops is an accessible and educational way to get involved in the crypto space, especially for beginners.
            Best of all, you can grow your portfolio with real value without investing money upfront.
            Browse our list of active airdrops, track new opportunities in real time, and start earning free crypto today!
            </p>
            <h2>About Me...</h2>
            <p>
            I am graduated in electrical-electronic engineering and D.Sc. in signal processing, with a deep passion for the world of investments.
            Throughout my career, I have had the opportunity to combine my technical knowledge with my curiosity about the financial universe,
            especially in the cryptocurrency and airdrop sectors.
            </p>
            <p>
            Over time, I have applied the lessons I learned in engineering to explore new investment opportunities.
            Additionally, I am a programming enthusiast, with an emphasis on Python, which was the language chosen for the development of this site.
            My goal is to use both my technical skills and financial experience to provide relevant content and efficient solutions for others
            who share the same interest in the world of crypto and investments.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        "<hr style='border: 2px double #342b44;'>",
        unsafe_allow_html=True
    )

elif opcao == "🌾 Farm with YT":
    # CSS personalizado para ajustar o tamanho da fonte da sidebar
    st.markdown("""
        <div style="
            background: radial-gradient(circle at top center, #2c2f35 0%, #1c1e22 100%);
            font-size: 25px;
            border: 2px solid #444; 
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
            padding: 25px;
            margin: 20px 0;
            color: white;
            font-family: 'Space Grotesk', sans-serif;
        ">
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
                <p>
                You need to adjust the Parameters to evaluate each Protocol, mainly the expected FDV in TGE. 
                Do not expect that a protocol with $30M TVL will be able to do an TGE with $100M of FDV, be coherent in your expectations.
                </p>
                <p>
                To apply new Parameters to ROI Estimation, click on <strong>"Refresh YT"</strong>.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Novo Quadro de Inputs ---
    st.sidebar.markdown("<h3 style='font-size: 20px;'>Parameters to YT ROI Estimation</h3>", unsafe_allow_html=True)
    with st.sidebar.expander("", expanded=True):
        invested = st.number_input("Choose the Value to Invest ($):", min_value=0.0, value=1000.0, step=1.0)
        tsp = st.number_input("Expected Token Total Supply (B):", min_value=0, value=1) * 1_000_000_000
        drop = st.number_input("Expected Percentual to Protocol Airdrop (%):", min_value=0.0, max_value=100.0, value=5.0)
        Level_fdv = st.number_input("Expected Level FDV in TGE ($M):", min_value=0, value=150, step=1) * 1_000_000
        #Open_fdv = st.number_input("Expected OpenEden FDV in TGE ($M):", min_value=0, value=200, step=1) * 1_000_000
        Frag_fdv = st.number_input("Expected Frag. FDV in TGE ($M):", min_value=0, value=400, step=1) * 1_000_000
        ky_fdv = st.number_input("Expected Kyros FDV in TGE ($M):", min_value=0, value=40, step=1) * 1_000_000
        Sp_fdv = st.number_input("Expected Spark FDV in TGE ($M):", min_value=0, value=300, step=1) * 1_000_000
        Gaib_fdv = st.number_input("Expected Gaib FDV in TGE ($M):", min_value=0, value=30, step=1) * 1_000_000

        st.markdown("---")
        Level_l_date = st.text_input(
            "Expected Level TGE Date:",
            value="2025-09-24",   # valor padrão
        )
        #Open_l_date = st.text_input(
        #    "Expected OpenEden TGE Date:",
        #    value="2025-09-30",   # valor padrão
        #)
        Frag_l_date = st.text_input(
            "Expected Fragmetric TGE Date:",
            value="2025-09-30",   # valor padrão
        )
        Ky_l_date = st.text_input(
            "Expected Kyros TGE Date:",
            value="2025-07-30",   # valor padrão
        )
        Sp_l_date = st.text_input(
            "Expected Sparks TGE Date:",
            value="2025-08-14",   # valor padrão
        )
        Gaib_l_date = st.text_input(
            "Expected Gaib TGE Date:",
            value="2025-08-14",   # valor padrão
        )

    # Botão
    update_button = st.button("Refresh YT")

    # Verifica se já se passaram 120 segundos
    if update_button or not protocolos or elapsed_seconds < 10:
        with st.spinner('Loading Data and Calculating Parameters...'):
            #try: 
            # Busca Informações no Defillama
            #Open_tvl,Open_amount,Open_leadInvestors,Open_otherInvestors = get_defillama_info("openeden","Ethereum")
            Level_tvl,Level_amount,Level_leadInvestors,Level_otherInvestors = get_defillama_info("level","Ethereum")
            Frag_tvl,Frag_amount,Frag_leadInvestors,Frag_otherInvestors = get_defillama_info("fragmetric","Solana")
            Ky_tvl,Ky_amount,Ky_leadInvestors,Ky_otherInvestors = get_defillama_info("kyros","Solana")
            Sp_tvl,Sp_amount,Sp_leadInvestors,Sp_otherInvestors = get_defillama_info("Spark","Ethereum")
            
            # Busca dados dos protocolos em suas respectivas API's
            tags, values, time_Open, time_Level,top100,total_users = enviar_dados()
            Frag_accured,Frag_unApy,solAsUSD,fragAsUSD,fragBySol,Frag_total_users = get_fragmetric_data()
            Ky_accured,Ky_unApy,KyAsUSD,Ky_total_users,Ky_top100p = get_leader_kyros_function()
            Sp_accured,Sp_top100p,Sp_total_users,Sp_tokens_per_day = get_Leader_Spark_Data()
            Gaib_accured,Gaib_top100p,Gaib_total_users,Gaib_tvl = get_leader_Gaib_function()
            
            # Busca dados dos protocolos nas API's da Pendle (Rede Ethereum) e Rate-X (Rede Solana)
            #Open_ytMul,Open_unApy,Open_impApy,Open_feeRate,Open_swapFee,Open_ytRoi,Open_expiry,Open_priceImpact = get_Pendle_Data("0xa77c0de4d26b7c97d1d42abd6733201206122e25","0x42E2BA2bAb73650442F0624297190fAb219BB5d5")
            Level_ytMul,Level_unApy,Level_impApy,Level_feeRate,Level_swapFee,Level_ytRoi,Level_expiry,Level_priceImpact = get_Pendle_Data("0xc88ff954d42d3e11d43b62523b3357847c29377c","0x47247749e976c54c6db2a9db68c5cadb05482e9f")
            Frag_ytMul,Frag_Multiplier,Frag_expiry,Frag_swapFee,Frag_priceImpact,time_Frag,symbol_frag = get_rateX_data("fragmetric")
            ky_ytMul,ky_Multiplier,ky_expiry,ky_swapFee,ky_priceImpact,time_ky,symbol_ky = get_rateX_data("kyros")
            Sp_ytMul,Sp_unApy,Sp_impApy,Sp_feeRate,Sp_swapFee,Sp_ytRoi,Sp_expiry,Sp_priceImpact = get_Pendle_Data("0xdace1121e10500e9e29d071f01593fd76b000f08","0x4eb0bb058bcfeac8a2b3c2fc3cae2b8ad7ff7f6e")
            Gaib_ytMul,Gaib_unApy,Gaib_impApy,Gaib_feeRate,Gaib_swapFee,Gaib_ytRoi,Gaib_expiry,Gaib_priceImpact = get_Pendle_Data("0x47306e3cb4e325042556864b38aa0cbe8d928be5","0x05db2d5f89b3e9eab8f9c07149cd3a7575db8b9d")

            # Formata a data atual e as datas de TGE (informadas pelo usuário) para que possam ser subtraídas
            date_obj = datetime.strptime(time_Open, "%Y-%m-%d %H:%M:%S")
            date_utc_formatada = date_obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            date1 = datetime.strptime(date_utc_formatada , "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            #date2 = datetime.strptime(Open_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            date3 = datetime.strptime(Level_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            date4 = datetime.strptime(Frag_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            date5 = datetime.strptime(ky_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            date6 = datetime.strptime(Sp_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            date7 = datetime.strptime(Gaib_expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            
            # Calcula os parâmetros de cada Protocolo
            # OpenEden
            #Open_date_tge = datetime.strptime((Open_l_date+"T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            #Open_mean_daily = 1.3*(values[0]-Open_TP_0)/((date1-Open_date0).days)
            #Open_points_tge = round(values[0] + (((Open_date_tge-date1).days)*Open_mean_daily),0)
            #Open_points_per_token = round(Open_points_tge/(tsp*drop/100),2)
            #Open_farmed_yield = round(invested*Open_ytMul*Open_unApy*(date2-date1).days/365,2)
            #Open_daily_pts_farmed = round(invested*Open_ytMul*Open_Multipleir*Open_Boost*Open_pts_token,2)
            #Open_total_pts_farmed = round(Open_daily_pts_farmed*(date2-date1).days,2)
            #Open_etimated_tokens = round(Open_total_pts_farmed/Open_points_per_token,2)
            #Open_airdrop_value = round((Open_fdv/tsp)*Open_etimated_tokens,2)
            #Open_cost = abs(round((Open_farmed_yield - invested - (invested*abs(Open_priceImpact))),2))
            #Open_profit = round((Open_airdrop_value - Open_cost),2)
            #Open_ROI = round((100*Open_profit/Open_cost),2)
            
            #Open_grade = protocol_rate(Open_tvl,(100*top100[0]),Open_ROI,(100*Open_mean_daily/values[0]),total_users[0],"bom")
            
            # Level
            Level_date_tge = datetime.strptime((Level_l_date+"T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            Level_mean_daily = 1.3*(values[1]-Level_TP_0)/((date1-Level_date0).days)
            Level_points_tge = round(values[1] + (((Level_date_tge-date1).days)*Level_mean_daily),0)
            Level_points_per_token = round(Level_points_tge/(tsp*drop/100),2)
            Level_farmed_yield = round(invested*Level_ytMul*Level_unApy*(date3-date1).days/365,2)
            Level_daily_pts_farmed = round(invested*Level_ytMul*Level_Multipleir*Level_Boost*Level_pts_token,2)
            Level_total_pts_farmed = round(Level_daily_pts_farmed*(date3-date1).days,2)
            Level_etimated_tokens = round(Level_total_pts_farmed/Level_points_per_token,2)
            Level_airdrop_value = round((Level_fdv/tsp)*Level_etimated_tokens,2)
            Level_cost = abs(round((Level_farmed_yield - invested - (invested*abs(Level_priceImpact))),2))
            Level_profit = round((Level_airdrop_value - Level_cost),2)
            Level_ROI = round((100*Level_profit/Level_cost),2)

            Level_grade = protocol_rate(Level_tvl,(100*top100[1]),Level_ROI,(100*Level_mean_daily/values[1]),total_users[1],"otimo")
            
            # Fragmetric
            Frag_date_tge = datetime.strptime((Frag_l_date+"T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            Frag_mean_daily = 1.3*(Frag_accured-Frag_TP_0)/((date1-Frag_date0).days)
            Frag_points_tge = round(Frag_accured + (((Frag_date_tge-date1).days)*Frag_mean_daily),0)
            Frag_points_per_token = round(Frag_points_tge/(tsp*drop/100),2)
            Frag_farmed_yield = round((invested)*Frag_ytMul*Frag_unApy*(date4-date1).days/365,2)
            Frag_daily_pts_farmed = round((invested/fragAsUSD)*Frag_ytMul*Frag_Multipleir*Frag_Boost*Backpack_Boost*Frag_pts_token,2)
            Frag_total_pts_farmed = round(Frag_daily_pts_farmed*(date4-date1).days,2)
            Frag_etimated_tokens = round(Frag_total_pts_farmed/Frag_points_per_token,2)
            Frag_airdrop_value = round((Frag_fdv/tsp)*Frag_etimated_tokens,2)
            Frag_cost = abs(round(((Frag_farmed_yield) - invested - abs(fragAsUSD*Frag_swapFee)),2))
            Frag_profit = round((Frag_airdrop_value - Frag_cost),2)
            Frag_ROI = round((100*Frag_profit/Frag_cost),2)

            Frag_grade = protocol_rate(Frag_tvl,60,Frag_ROI,(100*Frag_mean_daily/Frag_accured),Frag_total_users,"top")

            # Kyros
            Ky_date_tge = datetime.strptime((Ky_l_date+"T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            Ky_mean_daily = 1.3*(Ky_accured-Ky_TP_0)/((date1-Ky_date0).days)
            Ky_points_tge = round(Ky_accured + (((Ky_date_tge-date1).days)*Ky_mean_daily),0)
            Ky_points_per_token = round(Ky_points_tge/((tsp)*2*drop/100),2)
            Ky_farmed_yield = round((invested)*ky_ytMul*Ky_unApy*(date5-date1).days/365,2)
            Ky_daily_pts_farmed = round((invested/KyAsUSD)*ky_ytMul*Ky_Multipleir*Ky_Boost*ky_pts_token,2)
            Ky_total_pts_farmed = round(Ky_daily_pts_farmed*(date5-date1).days,2)
            Ky_etimated_tokens = round(Ky_total_pts_farmed/Ky_points_per_token,2)
            Ky_airdrop_value = round((ky_fdv/tsp)*Ky_etimated_tokens,2)
            Ky_cost = abs(round(((Ky_farmed_yield) - invested - abs(KyAsUSD*ky_swapFee)),2))
            Ky_profit = round((Ky_airdrop_value - Ky_cost),2)
            Ky_ROI = round((100*Ky_profit/Ky_cost),2)

            Ky_grade = protocol_rate(Ky_tvl,(100*Ky_top100p),Ky_ROI,(100*Ky_mean_daily/Ky_accured),Ky_total_users,"bom")

            # Spark
            Sp_date_tge = datetime.strptime((Sp_l_date+"T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            Sp_mean_daily = 1.3*(Sp_accured - Sp_TP_0)/((date1-Sp_date0).days)
            Sp_points_tge = round(Sp_accured + (((Sp_date_tge-date1).days)*Sp_mean_daily),0)
            Sp_points_per_token = round(Sp_points_tge/(10000000000*drop/100),2)
            Sp_farmed_yield = round(invested*Sp_ytMul*Sp_unApy*(date6-date1).days/365,2)
            Sp_daily_pts_farmed = round(invested*Sp_ytMul*Sp_Multipleir*Sp_Boost*Sp_pts_token,2)
            Sp_total_pts_farmed = round(Sp_daily_pts_farmed*(date6-date1).days,2)
            Sp_etimated_tokens = round(Sp_total_pts_farmed/Sp_points_per_token,2)
            Sp_airdrop_value = round((Sp_fdv/10000000000)*Sp_etimated_tokens,2)
            Sp_cost = abs(round((Sp_farmed_yield - invested - (invested*abs(Sp_priceImpact))),2))
            Sp_profit = round((Sp_airdrop_value - Sp_cost),2)
            Sp_ROI = round((100*Sp_profit/Sp_cost),2)

            Sp_grade = protocol_rate(Sp_tvl,(100*Sp_top100p),Sp_ROI,(100*Sp_mean_daily/Sp_accured),Sp_total_users,"muito bom")

            # Gaib
            Gaib_date_tge = datetime.strptime((Gaib_l_date+"T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            Gaib_mean_daily = 1.3*(Gaib_accured - Gaib_TP_0)/((date1-Gaib_date0).days)
            Gaib_points_tge = round(Gaib_accured + (((Gaib_date_tge-date1).days)*Gaib_mean_daily),0)
            Gaib_points_per_token = round(Gaib_points_tge/((tsp)*drop/100),2)
            Gaib_farmed_yield = round(invested*Gaib_ytMul*Sp_unApy*(date6-date1).days/365,2)
            Gaib_daily_pts_farmed = round(invested*Gaib_ytMul*Gaib_Multipleir*Gaib_Boost*Gaib_pts_token,2)
            Gaib_total_pts_farmed = round(Gaib_daily_pts_farmed*(date7-date1).days,2)
            Gaib_etimated_tokens = round(Gaib_total_pts_farmed/Gaib_points_per_token,2)
            Gaib_airdrop_value = round((Gaib_fdv/tsp)*Gaib_etimated_tokens,2)
            Gaib_cost = abs(round((Gaib_farmed_yield - invested - (invested*abs(Gaib_priceImpact))),2))
            Gaib_profit = round((Gaib_airdrop_value - Gaib_cost),2)
            Gaib_ROI = round((100*Gaib_profit/Gaib_cost),2)

            Gaib_grade = protocol_rate(Gaib_tvl,(100*Gaib_top100p),Gaib_ROI,(100*Gaib_mean_daily/Gaib_accured),Gaib_total_users,"muito bom")
            #except:
            #    print("Error in YT Data Request")

        protocolos = {
            "Level": {
                "Imagem": "https://raw.githubusercontent.com/Caio-Fl/Airdrop_Points/main/lev.jpg",
                "Logo": "https://pbs.twimg.com/profile_images/1811061996172840960/wy0N3CoS_400x400.jpg",
                "pureLink": "https://app.level.money/farm?referralCode=pwlblh",
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
                "Mean Daily Points": f"{round(Level_mean_daily,0)}",
                "Estimated Points in TGE": f"{round(Level_points_tge,0)}",
                "Points per Token": f"{Level_points_per_token}",
                "Estimated FDV in TGE": f"{Level_fdv}",
                "Estimated Token Price": f"$ {Level_fdv/tsp}",
                "Estimated Tokens Airdrop": f"{Level_etimated_tokens}",
                "Estimated Airdrop Value": f"$ {Level_airdrop_value}",
                "Expected Profit": f"$ {Level_profit}",
                "Expected ROI": f"{Level_ROI} %"      
            },
            "Fragmetric": {
                "Imagem": "https://raw.githubusercontent.com/Caio-Fl/Airdrop_Points/main/frag.jpg",
                "Logo": "https://pbs.twimg.com/profile_images/1887701999426412544/ok8QD_Gh_400x400.png",
                "pureLink": "https://app.fragmetric.xyz/referral?ref=77XL68",
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
                "Mean Daily Points": f"{round(Frag_mean_daily,0)}",
                "Estimated Points in TGE": f"{round(Frag_points_tge,0)}",
                "Points per Token": f"{Frag_points_per_token}",
                "Estimated FDV in TGE": f"{Frag_fdv}",
                "Estimated Token Price": f"$ {Frag_fdv/tsp}",
                "Estimated Tokens Airdrop": f"{Frag_etimated_tokens}",
                "Estimated Airdrop Value": f"$ {Frag_airdrop_value}",
                "Expected Profit": f"$ {Frag_profit}",
                "Expected ROI": f"{Frag_ROI} %"          
            },
            "Kyros": {
                "Imagem": "https://raw.githubusercontent.com/Caio-Fl/Airdrop_Points/main/kyros.jpg",
                "Logo": "https://pbs.twimg.com/profile_images/1847426788252590080/-Tb-I1Yl_400x400.jpg",
                "pureLink": "https://boost.kyros.fi/?ref=nq3orn",
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
                "Mean Daily Points": f"{round(Ky_mean_daily,0)}",
                "Estimated Points in TGE": f"{round(Ky_points_tge,0)}",
                "Points per Token": f"{Ky_points_per_token}",
                "Estimated FDV in TGE": f"{ky_fdv}",
                "Estimated Token Price": f"$ {ky_fdv/tsp}",
                "Estimated Tokens Airdrop": f"{Ky_etimated_tokens}",
                "Estimated Airdrop Value": f"$ {Ky_airdrop_value}",
                "Expected Profit": f"$ {Ky_profit}",
                "Expected ROI": f"{Ky_ROI} %"   
            },
            "Spark (T. Supply: 10 Bi)": {
                "Imagem": "https://pbs.twimg.com/profile_images/1856332015341084672/lF5ZZXRm_400x400.jpg",
                "Logo": "https://pbs.twimg.com/profile_images/1856332015341084672/lF5ZZXRm_400x400.jpg",
                "pureLink": "https://app.spark.fi/points/8KBVQB",
                "Link": "<a href='https://app.spark.fi/points/8KBVQB' target='_blank' style='color:#FFA500;'>More info</a> - <a href='https://app.pendle.finance/trade/markets/0xdace1121e10500e9e29d071f01593fd76b000f08/swap?view=yt&py=output&chain=ethereum&chart=apy&page=1&trades=orders' target='_blank'>🔗 Pendle </a>",
                "Grade": f"{Sp_grade}",
                "TVL": f"{Sp_tvl} M",
                "Last Update": f"{time_Level}",
                "Expiry": f"{date6.date()}",
                "Total Points Farmed": f"{round(Sp_accured,0)}",
                "YT Multiplier": f"{round(Sp_ytMul,3)}",
                "YT APY": f"{round(Sp_unApy*100,2)}",
                "Time Until Expiration": f"{(date6-date1)}",
                "Protocol YT Multiplier": f"{Sp_Multipleir}",
                "Protocol Referral Boost": f"{round((Sp_Boost-1),2)*100} %",
                "Equivalent YT Received": f"$ {round(invested*Sp_ytMul,2)}",
                "Daily Points Farmed": f"{Sp_daily_pts_farmed}",
                "Total Points Farmed in YT": f"{Sp_total_pts_farmed}",
                "Top 100 Concentration": f"{round(100*Sp_top100p,2)}",
                "Total User": f"{Sp_total_users}",
                "Farmed Yield in YT": f"$ {Sp_farmed_yield}",
                "Mean Daily Points": f"{round(Sp_mean_daily,0)}",
                "Estimated Points in TGE": f"{round(Sp_points_tge,0)}",
                "Points per Token": f"{Sp_points_per_token}",
                "Estimated FDV in TGE": f"{Sp_fdv}",
                "Estimated Token Price": f"$ {Sp_fdv/10000000000}",
                "Estimated Tokens Airdrop": f"{Sp_etimated_tokens}",
                "Estimated Airdrop Value": f"$ {Sp_airdrop_value}",
                "Expected Profit": f"$ {Sp_profit}",
                "Expected ROI": f"{Sp_ROI} %"      
            },
            "Gaib": {
                "Imagem": "https://pbs.twimg.com/profile_images/1882466326423470082/ZttuZmOg_400x400.jpg",
                "Logo": "https://pbs.twimg.com/profile_images/1882466326423470082/ZttuZmOg_400x400.jpg",
                "pureLink": "https://aid.gaib.ai/explore?invite=BF96D68D",
                "Link": "<a href='https://aid.gaib.ai/explore?invite=BF96D68D' target='_blank' style='color:#FFA500;'>More info</a> - <a href='https://app.pendle.finance/trade/markets/0x47306e3cb4e325042556864b38aa0cbe8d928be5/swap?view=yt&py=output&chain=ethereum' target='_blank'>🔗 Pendle </a>",
                "Grade": f"{Gaib_grade}",
                "TVL": f"{Gaib_tvl} M",
                "Last Update": f"{time_Level}",
                "Expiry": f"{date7.date()}",
                "Total Points Farmed": f"{round(Gaib_accured,0)}",
                "YT Multiplier": f"{round(Gaib_ytMul,3)}",
                "YT APY": f"{round(Gaib_unApy*100,2)}",
                "Time Until Expiration": f"{(date7-date1)}",
                "Protocol YT Multiplier": f"{Gaib_Multipleir}",
                "Protocol Referral Boost": f"{round((Gaib_Boost-1),2)*100} %",
                "Equivalent YT Received": f"$ {round(invested*Gaib_ytMul,2)}",
                "Daily Points Farmed": f"{Gaib_daily_pts_farmed}",
                "Total Points Farmed in YT": f"{Gaib_total_pts_farmed}",
                "Top 100 Concentration": f"{round(100*Gaib_top100p,2)}",
                "Total User": f"{Gaib_total_users}",
                "Farmed Yield in YT": f"$ {Gaib_farmed_yield}",
                "Mean Daily Points": f"{round(Gaib_mean_daily,0)}",
                "Estimated Points in TGE": f"{round(Gaib_points_tge,0)}",
                "Points per Token": f"{Gaib_points_per_token}",
                "Estimated FDV in TGE": f"{Gaib_fdv}",
                "Estimated Token Price": f"$ {Gaib_fdv/tsp}",
                "Estimated Tokens Airdrop": f"{Gaib_etimated_tokens}",
                "Estimated Airdrop Value": f"$ {Gaib_airdrop_value}",
                "Expected Profit": f"$ {Gaib_profit}",
                "Expected ROI": f"{Gaib_ROI} %"      
            }
        }
        
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
                    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 5px;font-size: 25px;">
                        <img src="{protocolos[p]['Logo']}" width="70" height="70" style="border-radius: 5%;">
                        <h4 style="margin: 5;font-size: 25px;color: #FFA500">{p}</h4>
                    </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(f"""
            <div style="background-color: #376a94; padding: 20px; border: 2px solid white; border-radius: 10px; margin-top: 20px; font-size: 25px;margin-bottom: 5px;">
                <h2>Details {p}</h2>
                    <p style="font-size:25px;">
                        <strong>Protocol:</strong> {p} – 
                        <a href= {protocolos[p]['pureLink']} target='_blank' style='color:#1E90FF;'>Visit Protocol</a>
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
                    <li><strong>Mean Daily Points:</strong> {protocolos[p]['Mean Daily Points']} XP</li>
                    <li><strong>Estimated Total Points in TGE:</strong> {protocolos[p]['Estimated Points in TGE']} XP</li>
                    <li><strong>Points to Receive 1 Token:</strong> {protocolos[p]['Points per Token']}</li>
                    <li><strong>Estimated FDV in TGE:</strong> {protocolos[p]['Estimated FDV in TGE']}</li>
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
        # Centraliza o conteúdo
        

        cols = st.columns(3, gap="large")
        for i, (nome, dados) in enumerate(protocolos.items()):
            with cols[i % 3]:
                st.markdown(f"""
                    <div style="
                        background: radial-gradient(circle at top center, #2c2f35 0%, #1c1e22 100%);
                        border: 3px double #555;
                        box-shadow: 
                            0 0 10px #00e0ff,
                            0 0 8px #00e0ff,
                            0 0 8px #00e0ff,
                            0 0 8px #00e0ff;
                        border-radius: 10px;
                        width: 100%;
                        padding: 20px;
                        margin: 15px 0;
                        color: white;
                        text-align: center;
                        font-family: 'Space Grotesk', sans-serif;
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                    ">
                        <div style="border: 2px solid #444; padding: 10px; radial-gradient(circle at top center, #2c2f35 0%, #1c1e22 100%); border-radius: 6px; margin: 15px 0; font-size: 25px;">
                            <img src="{dados['Logo']}" width="70" />
                            <div style="margin-top: 15px; font-weight: bold;">{nome}</div>
                            <div style="border: 2px solid #444; background: radial-gradient(circle at top center, #2c2f35 0%, #1c1e22 100%);border-radius: 16px;box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);padding: 10px; border-radius: 6px; margin: 15px 0; font-size: 22px; text-align: center;">
                                <p><strong>TVL:</strong> {dados['TVL']}</p>
                                <p><strong>Expected ROI:</strong> {dados['Expected ROI']}</p>
                                <p><strong>YT Multiplier:</strong> {dados['YT Multiplier']}</p>
                                <p><strong>YT APY:</strong> {dados['YT APY']} %</p>
                                <p><strong>Boost:</strong> {dados['Protocol Referral Boost']}</p>
                                <p><strong>Expiry:</strong> {dados['Expiry']}</p>
                                <p><strong>Rating:</strong> {dados['Grade']}</p>
                            </div>
                            <p href="{dados['pureLink']}" target="_blank">
                                <button style="
                                    background-color: orange;
                                    color: black;
                                    font-family: 'Space Grotesk', sans-serif;
                                    padding: 10px 20px;
                                    border: none;
                                    border-radius: 5px;
                                    font-size: 25px;
                                    cursor: pointer;
                                    margin-bottom: 10px;
                                "><strong>Visit Protocol</strong></button>
                            </p>
                            <button style="
                                background-color: #2e2b44;
                                font-family: 'Space Grotesk', sans-serif;
                                color: white;
                                padding: 8px 16px;
                                border: none;
                                border-radius: 5px;
                                font-size: 25px;
                                cursor: pointer;
                            ">View Details</button>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 2px double #342b44;'>", unsafe_allow_html=True)


elif opcao == "📈 Pendle APY Prediction":
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

    st.sidebar.markdown("<h3 style='font-size: 25px;'>Select Pendle Market</h3>", unsafe_allow_html=True)
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
        st.markdown(f"<span style='font-size:25px'><strong>Selected Market:</strong> {label}</span>", unsafe_allow_html=True)
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
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
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

            # TVL em eixo secundário
            fig.add_trace(go.Scatter(x=dates, y=tvl_in_k, mode='lines+markers', name='TVL (Mi USD)', line=dict(color='orange', dash='dot'), yaxis='y2'))

            # Linha vertical para expiry
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
                font=dict(size=20)  # Só o tamanho
            )

            # Layout com dois eixos y e fonte aumentada
            fig.update_layout(
                title=f'YT-{selected_row["name"]} {expiry_date.date()} - History of Base APY, Implied APY, Tendency Lines and TVL',
                
                xaxis_title='Date',
                xaxis=dict(
                    tickfont=dict(size=25)
                ),

                yaxis_title='APY (%)',
                yaxis=dict(
                    range=[0, None],
                    tickfont=dict(size=25)
                ),

                yaxis2=dict(
                    title='TVL (Mi USD)',
                    overlaying='y',
                    side='right',
                    tickfont=dict(size=20)
                ),

                legend=dict(
                    x=1,
                    y=1,
                    xanchor='right',
                    yanchor='top',
                    bgcolor='rgba(52,43,68,0.8)',
                    font=dict(size=20)
                ),

                font=dict(size=20),  # Fonte geral: aplica em títulos, anotações e eixos que não foram especificados

                plot_bgcolor='rgba(255, 255, 255, 1)',
                paper_bgcolor='rgba(52,43,68, 1)',
                hovermode='x unified',
                height=750
            )

            # Mostrar com zoom habilitado
            st.plotly_chart(fig, use_container_width=True)

        def normalizar_para_faixa(valor, min_origem=0, max_origem=100, min_dest=-100, max_dest=100):
            return min_dest + ((valor - min_origem) / (max_origem - min_origem)) * (max_dest - min_dest)

        valor = normalizar_para_faixa(round(actual_perc,2))
        figura = barra_compra_venda(valor,round(actual_perc,2))
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
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
            blocks_html = "<h2 style='font-size:25px;font-family: 'Space Grotesk', sans-serif; color:#E6EDF3;'>🧠 AI Interpretation:</h2>"
            for resposta in IA:
                resposta_html = resposta.replace("**", "&nbsp;").replace("\n", "<br>")
                blocks_html += f"""
                <div class="protocol-block">
                        st.plotly_chart(fig, use_container_width=True)
                        <p style="font-size: 25px;">{resposta_html}</p>
                </div>
                """   
        #else:
        #    st.markdown(IA)
    full_html = f"""
    <style>
    .container-externa {{
        border: 2px solid #444;
        border-radius: 16px;
        padding: 25px;
        margin-top: 30px;
        background: #212328;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        justify-content: center;
        display: flex;
        flex-direction: column;
        gap: 30px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
        color: white;
        margin: 20px 0;
    }}
    .protocol-block {{
        width: 2830px;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}
    .protocol-header {{
        margin-top: 20px;
        min-height: 70px;
        border: 3px solid #00e0ff;
        border-radius: 10px;
        padding: 10px;
        background: linear-gradient(0deg, #2a2238, #342b44, #4a3b5f);
        color: white;
        box-shadow: 0 0 10px #00e0ff, 0 0 8px #00e0ff;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
    }}
    .protocol-header .icon {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
    }}
    .protocol-footer {{
        border: 2px solid #00e0ff;
        style="flex-basis: 100%; height: 0;
        margin-bottom: 20px;
        min-height: 100px;
        border-radius: 10px;
        border: 2px solid #444; 
        background: radial-gradient(circle at top, #3a3d45 0%, #2a2b30 100%);
        box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.4);
        border-radius: 10px;
        padding: 10px; 
        border-radius: 10px;
        color: white;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
    }}
    .protocol-footer a {{
        color: lightblue;
        text-decoration: none;
    }}
    </style>

    <div class="container-externa">
        {blocks_html}
    </div>
    """

    components.html(full_html, height=800, scrolling=True)

    
    st.markdown("---")  # Linha separadora entre blocos

    st.markdown(
    """
    <style>
    .pendle-apy-description {
        border: 2px solid #444;
        border-radius: 16px;
        padding: 25px;
        margin-top: 30px;
        background: #212328;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        justify-content: left;
        display: flex;
        flex-direction: column;
        gap: 30px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
        color: white;
        margin: 20px 0;
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
    In addition, <strong>buying opportunities</strong> may arise when the Implied APY touches the <span style='color:red;'><strong>minimum green trend line</strong></span>,
    indicating a temporary undervaluation. Conversely, <strong>selling opportunities</strong> may be more favorable when the Implied APY reaches the <span style='color:red;'><strong>maximum red trend line</strong></span>,
    suggesting a potential overvaluation.
    </p>
    <p>
    This chart allows users to compare real and expected yields, monitor market sentiment, and identify attractive entry and exit points for Pendle pools.
    </p>
    </div>
    """,
    unsafe_allow_html=True
    )
    st.markdown(
        "<hr style='border: 2px double #342b44;'>",
        unsafe_allow_html=True
    )    
    
elif opcao == "🎁 Latest Airdrops":
    st.info("🚧 Coming Soon: Protocols with Airdrop Potential.")

elif opcao == "📡 Depin Airdrops":

    protocols_depin = [
        {"name":"Monad Score","priority":"S","funding":"Not disclosed","site":"https://dashboard.monadscore.xyz/signup/r/cWiIkvLG","social":{"twitter":"https://x.com/monadscores_xyz","discord":"https://discord.com/invite/rYGaM87RZV"},"status":"Active Farming","application":"Decentralized Reputation", "image":"https://pbs.twimg.com/profile_images/1898905479998287873/KqiFFod6_400x400.jpg"},
        {"name":"OpenLedger","priority":"S","funding":"Not disclosed","site":"https://testnet.openledger.xyz/?referral_code=fdhgyvakoq","social":{"twitter":"https://x.com/OpenledgerHQ","discord":"https://discord.gg/wfeSEqH8"},"status":"Active Farming","application":"AI Blockchain", "image":"https://pbs.twimg.com/profile_images/1876981396134416384/lYzcJz9J_400x400.jpg"}, 
        {"name":"Taker","priority":"A","funding":"$3M","site":"https://earn.taker.xyz?start=BXBDE7KR","social":{"twitter":"https://x.com/TakerProtocol","discord":"https://discord.gg/BkJy83ZT"},"status":"Active Farming","application":"Data Monetization Infra", "image":"https://pbs.twimg.com/profile_images/1905084157732257792/qIzxjm1A_400x400.jpg"},
        {"name":"Parasail","priority":"A","funding":"$4M","site":"https://www.parasail.network/season?refer=MHgzRTYyMTAxMkNiNjI3MmIwN2UwNTVhYTYyRjNBRTEyQzJBZGNDOTZG","social":{"twitter":"https://x.com/parasailnetwork","discord":"https://discord.com/invite/parasail"},"status":"Active Farming","application":"Private AI at the Edge", "image":"https://pbs.twimg.com/profile_images/1788203111720570880/RqVxPfmL_400x400.jpg"},
        {"name":"Rynus.io","priority":"S","funding":"Not disclosed","site":"https://cloud.rynus.io/login?affiliateId=BFD9FF25EC3B","social":{"twitter":"https://x.com/Rynus_io","discord":"https://discord.com/invite/Y3S8U8myeA"},"status":"Active Farming","application":"Distributed Computing", "image":"https://pbs.twimg.com/profile_images/1843848451177754629/JG9s95wv_400x400.jpg"},
        {"name":"Public AI","priority":"A","funding":"$2M","site":"https://beta.publicai.io/?r=eBoOF","social":{"twitter":"https://x.com/PublicAIData","discord":"https://discord.gg/JRaJFdmx"},"status":"Active Farming","application":"Decentralized AI Infrastructure", "image":"https://pbs.twimg.com/profile_images/1910358838764802048/3Mk5g06M_400x400.jpg"},
        {"name":"Uplink","priority":"S","funding":"$10M","site":"https://explorer.uplink.xyz/register?referralCode=XK7aY2","social":{"twitter":"https://x.com/uplink_xyz","discord":"https://discord.com/invite/r5d9DCT2e2"},"status":"Active Farming","application":"Decentralized Connectivity", "image":"https://pbs.twimg.com/profile_images/1897064849689227264/iOge47Am_400x400.jpg"},
        {"name":"Kaisar","priority":"A","funding":"$1M","site":"https://zero.kaisar.io/register?ref=GoGPgT669","social":{"twitter":"https://x.com/KaisarNetwork","discord":"https://discord.gg/fKHUPa72"},"status":"Active Farming","application":"Secure Connectivity & Identity", "image":"https://pbs.twimg.com/profile_images/1776202066282926080/5ppDFq9k_400x400.jpg"},
        {"name":"NodePay","priority":"S","funding":"$7M","site":"https://app.nodepay.ai/register?ref=0kKEtv5Z8Ae3yMv","social":{"twitter":"https://x.com/nodepay_ai","discord":"https://discord.gg/nodepay"},"status":"Season 3","application":"Sensor & Edge Devices","image": "https://pbs.twimg.com/profile_images/1785448882195013632/NlAWjldQ_400x400.jpg"},
        {"name":"Dawn","priority":"S","funding":"$18M","site":"(Code: dker3uap) https://chromewebstore.google.com/detail/dawn-validator-chrome-ext/fpdkjdnhkakefebpekbdhillbhonfjjp?authuser=0&hl=en","social":{"twitter":"https://x.com/dawninternet","discord":"https://discord.gg/jhPkKCZq"},"status":"Active Farming","application":"Data Storage / Web Browsing Data","image": "https://pbs.twimg.com/profile_images/1811363474284417025/3yGX3CjY_400x400.jpg"},
        {"name":"Grass","priority":"S","funding":"$4.5M","site":"https://app.getgrass.io/register?referralCode=XEQ1thjGfHk0N8O","social":{"twitter":"https://x.com/grass","discord":"https://discord.gg/getgrass"},"status":"Season 2","application":"Data Monetization (Web)", "image":"https://pbs.twimg.com/profile_images/1836126251007852545/wILJU3d6_400x400.jpg"},
        {"name":"3DOS","priority":"S","funding":"Not disclosed","site":"https://dashboard.3dos.io/register?ref_code=894a3e","social":{"twitter":"https://x.com/3DOSNetwork","discord":"https://discord.gg/3kE2yUxa"},"status":"Active Farming","application":"Distributed Manufacturing / IoT", "image":"https://pbs.twimg.com/profile_images/1616254196377952257/yUxZSRAX_400x400.jpg"},
        {"name":"Gradient","priority":"S","funding":"Not disclosed","site":"https://app.gradient.network/signup?code=VFKHU1","social":{"twitter":"https://x.com/Gradient_HQ","discord":"https://discord.com/invite/2MthdzVJX9"},"status":"Active Farming","application":"Edge Devices / Sensors", "image":"https://pbs.twimg.com/profile_images/1873672943965990913/nlVpEV72_400x400.jpg"},
        {"name":"Bless","priority":"A","funding":"$8M","site":"https://bless.network/dashboard?ref=2SPZLM","social":{"twitter":"https://x.com/theblessnetwork","discord":"https://discord.gg/blessnetwork"},"status":"Active Farming","application":"Edge Devices / Sensor Data", "image":"https://pbs.twimg.com/profile_images/1858647923212361728/GYk64f8U_400x400.jpg"},
        {"name":"Multisync","priority":"A","funding":"$2.2M","site":"https://multisynq.io/auth?referral=487a7ae52ccc7827","social":{"twitter":"https://x.com/multisynq","discord":"https://discord.com/invite/6Bvt8vx8NA"},"status":"Connection Only","application":"Device Synchronization", "image":"https://pbs.twimg.com/profile_images/1801808935286095873/CWDq9WfZ_400x400.jpg"},
        {"name":"GRID","priority":"A","funding":"$2.2M","site":"https://sso.getgrid.ai/registration?referral_code=fc126e7","social":{"twitter":"https://x.com/GetGridAi","discord":"https://discord.com/invite/fDs88WUNXS"},"status":"Connection Only","application":"AI training", "image":"https://pbs.twimg.com/profile_images/1798313490534555648/BET1sJNK_400x400.jpg"},
        {"name":"Stork","priority":"A","funding":"$4M","site":"https://chromewebstore.google.com/detail/stork-verify/knnliglhgkmlblppdejchidfihjnockl","social":{"twitter":"https://x.com/StorkOracle","discord":"https://discord.com/invite/storkoracle"},"status":"Active Farming","application":"Geolocation Data Distribution", "image":"https://pbs.twimg.com/profile_images/1899474008195637248/-nVBNuKn_400x400.jpg"},
        {"name":"Toggle","priority":"B","funding":"Not disclosed","site":"https://toggle.pro/sign-up/11a2f0c1-35b5-4cc9-89c7-6ae2157f0ff7","social":{"twitter":"https://x.com/toggle","discord":"https://discord.com/invite/DfCyzC7tB8"},"status":"Active Farming","application":"DePIN Connectivity", "image":"https://pbs.twimg.com/profile_images/1847181726973415424/8mw2mGXQ_400x400.png"},
        {"name":"BlockMesh","priority":"B","funding":"Not disclosed","site":"https://app.blockmesh.xyz/register?invite_code=925336ba-de36-4e8e-a8ab-ce645919ce27","social":{"twitter":"https://x.com/blockmesh_xyz","discord":"https://discord.com/invite/pwZWzCtGx4"},"status":"Active Farming","application":"Decentralized Communication", "image":"https://pbs.twimg.com/profile_images/1820702766026645504/mL-smILQ_400x400.jpg"},
        {"name":"Distribute AI","priority":"B","funding":"Not disclosed","site":"https://r.oasis.ai/4c858669677a0fe6","social":{"twitter":"https://x.com/distributeai","discord":"https://discord.gg/distributeai"},"status":"Airdrop Released - Waiting Season 2","application":"Data Privacy & Storage for AI", "image":"https://pbs.twimg.com/profile_images/1866227189122789376/Ic2w3fhw_400x400.jpg"},
        {"name":"GaeaAI","priority":"B","funding":"Not disclosed","site":"https://app.aigaea.net/register?ref=gaSC6trQ0WpqzZ","social":{"twitter":"https://x.com/aigaealabs","discord":"https://discord.com/invite/aigaea"},"status":"Active Farming","application":"AI Training & Data Collection", "image":"https://pbs.twimg.com/profile_images/1904422472902115328/OQd87AE6_400x400.png"},
        {"name":"Teneo (Code: uigsb)","priority":"B","funding":"Not disclosed","site":"https://bit.ly/teneo-community-node","social":{"twitter":"https://x.com/teneo_protocol","discord":"https://discord.gg/teneoprotocol"},"status":"Active Farming","application":"DePIN Points + Data Contribution", "image":"https://pbs.twimg.com/profile_images/1797649020564754432/0Oav1zjU_400x400.jpg"},
        {"name":"Depinned (Code: DES9xJKEsKLfo2)","priority":"C","funding":"Not disclosed","site":"https://chromewebstore.google.com/detail/depined/pjlappmodaidbdjhmhifbnnmmkkicjoc?hl=pt-BR","social":{"twitter":"https://x.com/DePINed_org","discord":"https://discord.com/invite/74dEq5Et"},"status":"Active Farming","application":"Unclear / Browser Plugin", "image":"https://pbs.twimg.com/profile_images/1871083685732061184/GklrQE2V_400x400.jpg"},
        {"name":"Kleo Network","priority":"C","funding":"Not disclosed","site":"https://chromewebstore.google.com/detail/kleo-network/jimpblheogbjfgajkccdoehjfadmimoo?refAddress=0xb905B5F5869F6F6b6FC3C92950ec5bE210585f98","social":{"twitter":"https://x.com/kleo_network","discord":"discord.gg/4JQyXqBg8b"},"status":"Active Farming","application":"Private Storage Network", "image":"https://pbs.twimg.com/profile_images/1864932989756694528/M11KSBsP_400x400.jpg"},
    ]
    
    # Gera os blocos HTML individualmente
    blocks_html = ""
    for protocol in protocols_depin:
        blocks_html += f"""
        <div class="protocol-block">
            <div class="protocol-header">
                <img src="{protocol['image']}" width="50" height="50" style="border-radius: 50%;">
                <strong style="color: #FFA500;">{protocol['name']}</strong>
            </div>
            <div class="protocol-footer">
                <p style="font-size: 25px;"><strong>📌 Priority:</strong> {protocol['priority']}</p>
                <p style="font-size: 25px;"><strong>💰 Funding:</strong> {protocol['funding']}</p>
                <p style="font-size: 25px;"><strong>🚀 Application:</strong> {protocol['application']}</p>
                <p style="font-size: 25px;"><strong>📊 Status:</strong> {protocol['status']}</p>
                <p style="font-size: 25px;"><strong>📣 Social:</strong> 
                    <a href="{protocol['social']['twitter']}" style="color: lightblue;" target="_blank">Twitter</a> | 
                    <a href="{protocol['social']['discord']}" style="color: lightblue;" target="_blank">Discord</a>
                </p>
                <p style="font-size: 25px;"><strong>🌐 Site:</strong> <a href="{protocol['site']}" style="color: lightblue;" target="_blank">Visit Protocol</a></p>
            </div>
        </div>
        """

    # HTML completo
    full_html = f"""
    <style>
    .container-externa {{
        border: 2px solid #444;
        border-radius: 16px;
        padding: 25px;
        margin-top: 30px;
        background: #212328;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        justify-content: center;
        display: flex;
        flex-wrap: wrap;
        gap: 30px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
        color: white;
        margin: 20px 0;
    }}
    .protocol-block {{
        width: 683px;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}
    .protocol-header {{
        margin-top: 20px;
        min-height: 70px;
        border: 3px solid #00e0ff;
        border-radius: 10px;
        padding: 10px;
        background: linear-gradient(0deg, #2a2238, #342b44, #4a3b5f);
        color: white;
        box-shadow: 0 0 10px #00e0ff, 0 0 8px #00e0ff;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
    }}
    .protocol-header .icon {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
    }}
    .protocol-footer {{
        border: 2px solid #00e0ff;
        style="flex-basis: 100%; height: 0;
        margin-bottom: 20px;
        min-height: 100px;
        border-radius: 10px;
        border: 2px solid #444; 
        background: radial-gradient(circle at top, #3a3d45 0%, #2a2b30 100%);
        box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.4);
        border-radius: 10px;
        padding: 10px; 
        border-radius: 10px;
        color: white;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
    }}
    .protocol-footer a {{
        color: lightblue;
        text-decoration: none;
    }}
    </style>

    <div class="container-externa">
        {blocks_html}
    </div>
    """

    components.html(full_html, height=3600, scrolling=True)

    st.markdown(
        "<hr style='border: 2px double #342b44;'>",
        unsafe_allow_html=True
    )

elif opcao == "📊 Comparative YT Table":

    st.markdown(
        """
        <style>
        .bridge-description {
            font-size: 25px;
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
        "Mean Daily Points (XP)": [protocolos[p]["Mean Daily Points"] for p in protocolos],
        "Points in TGE (XP)": [protocolos[p]["Estimated Points in TGE"] for p in protocolos],
        "Points per Token": [protocolos[p]["Points per Token"] for p in protocolos],
        "Estimated FDV in TGE": [protocolos[p]["Estimated FDV in TGE"] for p in protocolos],
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
        .map(lambda v: 'color: green' if isinstance(v, (int, float)) and v > 0.1 else 'color: #E6EDF3')
        .set_table_styles([
            {
                "selector": "th.row_heading", 
                "props": [("color", "white"), ("background-color", "#342b44"), ("font-weight", "bold"), ("font-size", "25px")]
            },
            {
                "selector": "th.col_heading", 
                "props": [("color", "white"), ("background-color", "#342b44"), ("font-weight", "bold"), ("font-size", "25px")]
            },
            {
                "selector": "td",  # Aqui é o corpo da tabela
                "props": [("color", "#342b44"), ("background-color", "#E6EDF3"), ("font-size", "20px"), ("padding", "6px 12px"),("font-weight", "bold")]
            }
        ])
    )
    #st.write(styled_dfT)
    # Mostrando no Streamlit
    #st.dataframe(df, use_container_width=True)
    styled_df = df.style.applymap(
        lambda v: 'color: #342b44; background-color: #E6EDF3' if isinstance(v, (int, float)) and v > 0.1 
        else 'color: #342b44; background-color: #E6EDF3'
    )
    st.markdown("""
    <style>
    /* Fonte e cor das abas */
    .stTabs [data-baseweb="tab"] {
        font-size: 20px;
        font-family: 'Space Grotesk', sans-serif;
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
    
    st.markdown(
        "<hr style='border: 2px double #342b44;'>",
        unsafe_allow_html=True
    )

elif opcao == "✅ Last Claims and Checkers":
    code = "MTIyMTI1MjYwNzQxNTE1Njc3MA.Gg8_XS"
    code2=".BGfC4ic2rEyvs0bPk_jh3DSxRTNTlfbYZOjY34"
    
    headers = {
        "Authorization" : code+code2
    }
    
    Request_URL = "https://discord.com/api/v9/channels/1314347387942211605/messages?limit=5"
    res, org_res, org_author, org_mention, org_author_name = retrieve_messages(Request_URL,headers)

    respostas = mirror_list(org_res)

    Resp_sem_tag = [item.replace("<@&1291085400336760864>", "") for item in respostas]

    question = "\n\n".join(Resp_sem_tag)
    personality = """Translate to english and Rewrite the present text in a topic structure in few lines. Do not show topic structure title ang ignore content with X(twitter)"""

    result = mistral_AI_2(question,"ingles","mistral-large-latest",personality)
    
    # IA pode ser uma lista de dicionários com 'content'
    def markdown_to_html(texto):
        # Negrito em HTML
        texto = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', texto)

        # Substitui [qualquer coisa](link) por apenas o link com texto fixo
        texto = re.sub(r'\[.*?\]\((https?://[^\s]+)\)', r'<a href="\1" target="_blank" style="color: #ffd700;">Check Link</a>', texto)

        # Substitui links puros (sem markdown) por links com texto fixo também
        texto = re.sub(r'(?<!["=])\bhttps?://[^\s<]+', lambda match: f'<a href="{match.group(0)}" target="_blank" style="color: #ffd700;">Check Link</a>', texto)

        # Substituir quebras de linha por <br>
        return texto.replace('\n', '<br>')

    # Obter conteúdo e dividir pelos separadores
    blocos = result['content'].strip().split('\n\n')

    time.sleep(3)

        # Gera os blocos HTML individualmente
    blocks_html = ""
    texto_html = ""
    for i, bloco in enumerate(blocos):
        texto_html += markdown_to_html(bloco)
        texto_html += "<br><br>"
    blocks_html =f"""
        <div style='
            align-items: left;
            margin-bottom: 30px;
            justify-content: left;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 25px;
            gap: 30px;
            width: 2000px;
            display: flex; 
            flex-direction: column;
        '>
            {texto_html}
        </div>
        <div style="height: 40px;"></div>
        """

    # HTML completo
    full_html = f"""
    <style>
    .container-externa {{
        border: 2px solid #444;
        border-radius: 16px;
        padding: 25px;
        margin-top: 30px;
        background: #212328;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        display: flex;
        flex-wrap: wrap;
        gap: 30px;
        justify-content: left;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
        color: white;
        margin: 20px 0;
    }}
    .protocol-block {{
        width: 2000px;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}
    .protocol-header {{
        margin-top: 20px;
        min-height: 70px;
        border: 3px solid #00e0ff;
        border-radius: 10px;
        padding: 10px;
        background: linear-gradient(0deg, #2a2238, #342b44, #4a3b5f);
        color: white;
        box-shadow: 0 0 10px #00e0ff, 0 0 8px #00e0ff;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
    }}
    .protocol-header .icon {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
    }}
    .protocol-footer {{
        border: 2px solid #00e0ff;
        style="flex-basis: 100%; height: 0;
        margin-bottom: 20px;
        min-height: 100px;
        border-radius: 10px;
        border: 2px solid #444; 
        background: radial-gradient(circle at top, #3a3d45 0%, #2a2b30 100%);
        box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.4);
        border-radius: 10px;
        padding: 10px; 
        border-radius: 10px;
        color: white;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
    }}
    .protocol-footer a {{
        color: lightblue;
        text-decoration: none;
    }}
    </style>

    <div class="container-externa">
        {blocks_html}
    </div>
    """
    components.html(full_html, height=2850, scrolling=True)

    st.markdown(
        "<hr style='border: 2px double #342b44;'>",
        unsafe_allow_html=True
    )

elif opcao == "🌉 Bridges & Swaps Protocols":
    # Updated protocols data including Sonic and Hyperlane networks

    st.markdown(
        """
        <style>
        .bridge-description {
            border: 2px solid #444;
            border-radius: 16px;
            padding: 25px;
            margin-top: 30px;       
            background: #212328;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
            margin: 30px 0;
            color: white;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 25px;
            line-height: 1.7;
            text-align: justify;
            margin-bottom: 30px;
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
            {"name": "Jumper Exchange", "site": "https://jumper.exchange", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1930642162984579072/NtYd0Egd_400x400.png"},
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
            {"name": "Portal Bridge", "site": "https://portalbridge.com", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1927411080172593152/n_qpHIq7_400x400.jpg"},
            {"name": "Mayan", "site": "https://swap.mayan.finance/", "fees": "High", "image": "https://pbs.twimg.com/profile_images/1891499635597856769/5BMo_JQJ_400x400.jpg"},
            {"name": "Orbiter Finance", "site": "https://www.orbiter.finance/?channel=0xa786817be0b3fc4385e9f93140b513c9846c6f74", "fees": "High", "image": "https://pbs.twimg.com/profile_images/1880886737221664768/_uBH9pgt_400x400.jpg"},
            {"name": "Owlto", "site": "https://owlto.finance/?ref=0xa786817bE0B3FC4385E9F93140B513c9846C6f74", "fees": "Very High", "image": "https://pbs.twimg.com/profile_images/1886736859054923778/Iv098oCX_400x400.jpg"},
            {"name": "deBridge", "site": "https://debridge.finance", "fees": "Very High", "image": "https://pbs.twimg.com/profile_images/1894665537466040320/5vQrjq6M_400x400.jpg"},
        ],
        "Sui": [
            {"name": "Bridge.sui", "site": "https://bridge.sui.io/", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1928528183466373120/4xpp6RSr_400x400.jpg"},
            {"name": "Aftermath (Sui)", "site": "https://aftermath.finance/trade?", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1898807230818078720/g20J2FLu_400x400.jpg"},
            {"name": "7k (Sui)", "site": "https://7k.ag/?ref=6ZG45VKF2W", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1925943394586468352/uSHSEZ7M_400x400.jpg"},
            {"name": "Portal Bridge", "site": "https://portalbridge.com", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1927411080172593152/n_qpHIq7_400x400.jpg"},
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
            {"name": "Jumper Exchange", "site": "https://jumper.exchange",  "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1930642162984579072/NtYd0Egd_400x400.png"},
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
    st.sidebar.markdown("<h3 style='font-size: 25px;font-family: 'Space Grotesk', sans-serif;'>Select Network</h3>", unsafe_allow_html=True)
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
            "Network:",
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
    
    st.markdown("""
        <style>
            .custom-header {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 25px;
                font-weight: 600;
                color: white;
                margin-bottom: 5px;
                margin-left: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Exibir texto com a fonte Sora
    st.markdown(f'<div class="custom-header">   {selected_network.upper()}</div>', unsafe_allow_html=True)
    
    # Gera os blocos HTML individualmente
    blocks_html = ""
    for protocol in protocols_bridge_swap[selected_network]:
        blocks_html += f"""
        <div class="protocol-block">
            <div class="protocol-header">
                <img src="{protocol['image']}" width="50" height="50" style="border-radius: 50%;">
                <strong style="color: #FFA500;">{protocol['name']}</strong>
            </div>
            <div class="protocol-footer">
                <p style="font-size: 25px;">💸 Fees: {protocol['fees']} </p>
                <p style="font-size: 25px;">🌐 Site: <a href="{protocol['site']}" style="color: lightblue; font-size: 30px;" target="_blank">Visit Protocol</a></p>
            </div>
        </div>
        """

    # HTML completo
    full_html = f"""
    <style>
    .container-externa {{
        border: 2px solid #444;
        border-radius: 16px;
        padding: 25px;
        margin-top: 30px;
        background: #212328;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        display: flex;
        flex-wrap: wrap;
        gap: 30px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
        color: white;
        margin: 20px 0;
    }}
    .protocol-block {{
        width: 683px;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}
    .protocol-header {{
        margin-top: 20px;
        min-height: 70px;
        border: 3px solid #00e0ff;
        border-radius: 10px;
        padding: 10px;
        background: linear-gradient(0deg, #2a2238, #342b44, #4a3b5f);
        color: white;
        box-shadow: 0 0 10px #00e0ff, 0 0 8px #00e0ff;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
    }}
    .protocol-header .icon {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
    }}
    .protocol-footer {{
        border: 2px solid #00e0ff;
        style="flex-basis: 100%; height: 0;
        margin-bottom: 20px;
        min-height: 100px;
        border-radius: 10px;
        border: 2px solid #444; 
        background: radial-gradient(circle at top, #3a3d45 0%, #2a2b30 100%);
        box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.4);
        border-radius: 10px;
        padding: 10px; 
        border-radius: 10px;
        color: white;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
    }}
    .protocol-footer a {{
        color: lightblue;
        text-decoration: none;
    }}
    </style>

    <div class="container-externa">
        {blocks_html}
    </div>
    """

    components.html(full_html, height=2600, scrolling=True)
    st.markdown(
        "<hr style='border: 2px double #342b44;'>",
        unsafe_allow_html=True
    )

elif opcao == "🚰 Faucets":
    st.markdown(
        """
        <style>
        .bridge-description {
            border: 2px solid #444;
            border-radius: 16px;
            padding: 25px;
            margin-top: 30px;       
            background: #212328;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
            margin: 30px 0;
            color: white;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 25px;
            line-height: 1.7;
            text-align: justify;
        }
        </style>

        <div class="bridge-description">
            Below are some links to obtain Faucet tokens to support some protocols that may require faucets on their farms.
        </div>
        """,
        unsafe_allow_html=True
    )
    faucet_sites = [
        {"network": "Ethereum", "token": "ETH (Sepolia, Holesky)", "image":"https://pbs.twimg.com/profile_images/1878738447067652096/tXQbWfpf_400x400.jpg", "sites": ["https://sepolia-faucet.pk910.de/","https://faucet.hoodscan.io/", "https://console.optimism.io/faucet","",""]},
        {"network": "Bitcoin", "token": "BTC (Signet)", "image":"https://pbs.twimg.com/profile_images/421692600446619648/dWAbC2wg_400x400.jpeg", "sites": ["https://faucet.hoodscan.io/","","","",""]},
        {"network": "0G Labs", "token": "0G", "image":"https://pbs.twimg.com/profile_images/1933474287027171329/L-I1k2oL_400x400.jpg", "sites": ["https://faucet.0g.ai/","","","",""]},
        {"network": "Pharos", "token": "Pharos", "image":"https://pbs.twimg.com/profile_images/1899385457047412736/vfvmbKVj_400x400.jpg", "sites": ["https://testnet.pharosnetwork.xyz/", "https://zan.top/faucet/pharos", "https://web3.okx.com/pt-br/faucet","",""]},
        {"network": "Opnet", "token": "Opnet", "image":"https://pbs.twimg.com/profile_images/1817743953627660289/7HObLZyL_400x400.jpg", "sites": ["https://faucet.opnet.org","","","",""]},
        {"network": "Campnetwork", "token": "Campnetwork", "image":"https://pbs.twimg.com/profile_images/1774932612160557056/QOyzwbO2_400x400.jpg", "sites": ["https://faucet.campnetwork.xyz","","","",""]},
        {"network": "Somnia", "token": "Somnia", "image":"https://pbs.twimg.com/profile_images/1896736794810458112/9tsFttK2_400x400.jpg", "sites": ["https://testnet.somnia.network/","","","",""]},
        {"network": "Moonveil", "token": "Moonveil", "image":"https://pbs.twimg.com/profile_images/1789490763933577216/njozvdjD_400x400.jpg", "sites": ["https://faucet.testnet.moonveil.gg/","","","",""]},
        {"network": "Sahara", "token": "Sahara", "image":"https://pbs.twimg.com/profile_images/1871431718198239232/2LNyhe05_400x400.jpg", "sites": ["https://faucet.saharalabs.ai/", "https://web3.okx.com/pt-br/faucet","","",""]},
        {"network": "MegaETH", "token": "MegaETH", "image":"https://pbs.twimg.com/profile_images/1861751545790070784/KvlxTzAq_400x400.jpg", "sites": ["https://testnet.megaeth.com/#1","","","",""]},
        {"network": "Xion", "token": "Xion", "image":"https://pbs.twimg.com/profile_images/1881756422507024384/Huw5cTrb_400x400.jpg", "sites": ["https://faucet.xion.burnt.com/", "https://web3.okx.com/pt-br/faucet","","",""]},
        {"network": "AVAX", "token": "AVAX", "image":"https://pbs.twimg.com/profile_images/1923466301227532288/TuL8kPq3_400x400.jpg", "sites": ["https://core.app/tools/testnet-faucet/?subnet=c&token=c","","","",""]},
        {"network": "Seismic", "token": "Seismic", "image":"https://pbs.twimg.com/profile_images/1889153006483935233/VWQ-F4dG_400x400.png", "sites": ["https://faucet-2.seismicdev.net/","","","",""]},
        {"network": "Humanity", "token": "Humanity", "image":"https://pbs.twimg.com/profile_images/1923385112172888065/Elwahdp2_400x400.jpg", "sites": ["https://faucets.alchemy.com/faucets/humanity-testnet","","","",""]},
        {"network": "Monad", "token": "Monad", "image":"https://pbs.twimg.com/profile_images/1877532281419739137/I_t8rg_V_400x400.jpg", "sites": ["https://testnet.monad.xyz/", "https://stake.apr.io/faucet", "https://faucet.quicknode.com/", "https://thirdweb.com/monad-testnet",""]},
        {"network": "Sui", "token": "SUI", "image":"https://pbs.twimg.com/profile_images/1928528183466373120/4xpp6RSr_400x400.jpg", "sites": ["https://faucet.sui.io/","https://faucet.blockbolt.io/","","",""]},
        {"network": "Ethereum", "token": "USDC, EURC (Sepolia)", "image":"https://pbs.twimg.com/profile_images/1878738447067652096/tXQbWfpf_400x400.jpg", "sites": ["https://faucet.circle.com/","","","",""]},
        {"network": "Sei", "token": "SEI", "image":"https://pbs.twimg.com/profile_images/1873839225914716160/w8650_qp_400x400.jpg", "sites": ["https://www.docs.sei.io/learn/faucet","","","",""]},
        {"network": "Babylon", "token": "Babylon Testnet", "image":"https://pbs.twimg.com/profile_images/1877578455576948736/q0GnBs9F_400x400.jpg", "sites": ["https://faucet.hoodscan.io/","","","",""]},
        {"network": "Google Web3 Faucet", "token": "ETH, Holesky, ZetaChain, Injective, Mantra, Story Aeneid, PYUSD ETH & Solana", "image":"https://pbs.twimg.com/profile_images/1754606338460487681/bWupXdxo_400x400.jpg", "sites": ["https://cloud.google.com/application/web3/faucet","","",""]},
        {"network": "Chainlink", "token": "Multichain", "image":"https://pbs.twimg.com/profile_images/1800426318099595264/N7yf_kOD_400x400.jpg", "sites": ["https://faucets.chain.link/","","","",""]},
        {"network": "Alchemy", "token": "Multichain", "image":"https://pbs.twimg.com/profile_images/1876056405012033536/vjO9FucE_400x400.jpg", "sites": ["https://www.alchemy.com/faucets","","","",""]},
        {"network": "Quicknode", "token": "Multichain", "image":"https://pbs.twimg.com/profile_images/1875136807781662720/MJP7n4UN_400x400.jpg", "sites": ["https://faucet.quicknode.com/","","","",""]},
        {"network": "Buy Faucets", "token": "Multichain", "image":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSA131noMEukSs7KjDfFB7fURfU_mkHSZVmWw&s", "sites": ["https://www.gas.zip/", "https://testnetbridge.com/sepolia","","",""]}
    ]
  
    # Gera os blocos HTML individualmente
    blocks_html = ""
    for protocol in faucet_sites:
        blocks_html += f"""
        <div class="protocol-block">
            <div class="protocol-header">
                <img src="{protocol['image']}" width="50" height="50" style="border-radius: 50%;">
                <strong style="color: #FFA500;">{protocol['network']}</strong>
            </div>
            <div class="protocol-footer">
                <p><strong>🪙 Token: {protocol['token']}</strong></p>
                <strong>🌐 Sites: </strong><br>
                {"<br>".join([f'<a href="{site}" target="_blank" style="color: lightblue;">&emsp;&emsp;{site}</a>' for site in protocol['sites']])}
            </div>
        </div>
        """

    # HTML completo
    full_html = f"""
    <style>
    .container-externa {{
        border: 2px solid #444;
        border-radius: 16px;
        padding: 25px;
        margin-top: 30px;
        background: #212328;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        display: flex;
        flex-wrap: wrap;
        gap: 30px;
        justify-content: center;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
        color: white;
        margin: 20px 0;
    }}
    .protocol-block {{
        width: 683px;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}
    .protocol-header {{
        margin-top: 20px;
        min-height: 70px;
        border: 3px solid #00e0ff;
        border-radius: 10px;
        padding: 10px;
        background: linear-gradient(0deg, #2a2238, #342b44, #4a3b5f);
        color: white;
        box-shadow: 0 0 10px #00e0ff, 0 0 8px #00e0ff;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
    }}
    .protocol-header .icon {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
    }}
    .protocol-footer {{
        border: 2px solid #00e0ff;
        style="flex-basis: 100%; height: 0;
        margin-bottom: 20px;
        min-height: 100px;
        border-radius: 10px;
        border: 2px solid #444; 
        background: radial-gradient(circle at top, #3a3d45 0%, #2a2b30 100%);
        box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.4);
        border-radius: 10px;
        padding: 10px; 
        border-radius: 10px;
        color: white;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
    }}
    .protocol-footer a {{
        color: lightblue;
        text-decoration: none;
    }}
    </style>

    <div class="container-externa">
        {blocks_html}
    </div>
    """

    components.html(full_html, height=2850, scrolling=True)

    st.markdown(
        "<hr style='border: 2px double #342b44;'>",
        unsafe_allow_html=True
    )

elif opcao == "⛔ Revoke Contract":

    st.markdown(
        """
        <style>
        .bridge-description {
            border: 2px solid #444;
            border-radius: 16px;
            padding: 25px;
            margin-top: 30px;       
            background: #212328;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
            margin: 30px 0;
            color: white;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 25px;
            line-height: 1.7;
            text-align: justify;
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
                font-size: 25px;
            }
            </style>
        """, unsafe_allow_html=True)
        selected_network = st.selectbox(
            "Network:",
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
    
    st.markdown("""
        <style>
            .custom-header {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 25px;
                font-weight: 600;
                color: white;
                margin-bottom: 5px;
                margin-left: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Exibir texto com a fonte Sora
    st.markdown(f'<div class="custom-header">   {selected_network.upper()}</div>', unsafe_allow_html=True)
    
    

    # Gera os blocos HTML individualmente
    blocks_html = ""
    for protocol in protocols_revoke[selected_network]:
        blocks_html += f"""
        <div class="protocol-block">
            <div class="protocol-header">
                <img src="{protocol['image']}" width="50" height="50" style="border-radius: 50%;">
                <strong style="color: #FFA500;">{protocol['name']}</strong>
            </div>
            <div class="protocol-footer">
                <br>
                🌐 Site: <a href="{protocol['site']}" target="_blank">{protocol['site']}</a>
            </div>
        </div>
        """
    

    # HTML completo
    full_html = f"""
    <style>
    .container-externa {{
        border: 2px solid #444;
        border-radius: 12px;
        padding: 25px;
        margin-top: 30px;
        background: #212328;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        display: flex;
        flex-wrap: wrap;
        gap: 30px;
        justify-content: flex-start;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
        color: white;
        margin: 20px 0;
    }}
    .protocol-block {{
        width: 684px;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}
    .protocol-header {{
        margin-top: 20px;
        min-height: 70px;
        border: 3px solid #00e0ff;
        border-radius: 10px;
        padding: 10px;
        background: linear-gradient(0deg, #2a2238, #342b44, #4a3b5f);
        color: white;
        box-shadow: 0 0 10px #00e0ff, 0 0 8px #00e0ff;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
    }}
    .protocol-header .icon {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
    }}
    .protocol-footer {{
        border: 2px solid #00e0ff;
        style="flex-basis: 100%; height: 0;
        margin-bottom: 20px;
        min-height: 100px;
        border-radius: 10px;
        border: 2px solid #444; 
        background: radial-gradient(circle at top, #3a3d45 0%, #2a2b30 100%);
        box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.4);
        border-radius: 16px;
        padding: 10px; 
        border-radius: 10px;
        color: white;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
    }}
    .protocol-footer a {{
        color: lightblue;
        text-decoration: none;
    }}
    </style>

    <div class="container-externa">
        {blocks_html}
    </div>
    """

    components.html(full_html, height=500, scrolling=True)

    st.markdown(
        "<hr style='border: 2px double #342b44;'>",
        unsafe_allow_html=True
    )

elif opcao == "⚠️ Avoiding Scams":

    st.markdown(
        """
        <style>
            .scam-warning-box {
                background: #212328;
                border: 3px double #ff7b00;
                box-shadow: 0 0 15px #ff7b00, 0 0 5px #ff7b00 inset;
                border-radius: 16px;
                padding: 40px;
                margin: 30px 0;
                color: white;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 25px;
                line-height: 1.7;
                text-align: justify;
            }
            .scam-warning-box h2 {
                color: #ffae42;
                font-size: 28px;
                margin-top: 30px;
            }
            .scam-warning-box ul {
                margin-left: 25px;
                margin-bottom: 25px;
            }
            .scam-warning-box a {
                color: #ffae42;
                text-decoration: none;
            }
            .scam-warning-box a:hover {
                text-decoration: underline;
            }
        </style>

        <div class="scam-warning-box">
            <p><strong>With the rise of crypto airdrops, scams have become more widespread than ever.</strong></p>
            <p>
            Many users rush to be among the first to discover new projects or engage with X posts to secure rewards. But that urgency can come at a high cost.
            Without careful verification, it’s easy to fall into traps set by scammers.
            They’ll use every trick in the book — from fake comments under posts to direct messages promising “great opportunities” — all designed to trick you and steal your funds.
            </p>
            <h2>🚨 How to Avoid Crypto Airdrop Scams</h2>
            <p>Crypto airdrops can be a great way to earn rewards—but they're also a big target for scammers. Here's a quick guide to staying safe while chasing drops.</p>
            <h2>🔒 1. Use a Dedicated Wallet for Airdrops</h2>
            <ul>
                <li><b>Create a separate wallet</b> just for airdrop interactions. Consider a Cold Wallet with at least 3 accounts by network.</li>
                <li><b>Never use your main wallet</b> with valuable assets.</li>
                <li>If anything goes wrong, your main funds stay safe.</li>
            </ul>
            <h2>🧠 2. Research Before You Click</h2>
            <ul>
                <li><b>Verify the project’s legitimacy</b> through <b>official sites</b> and <b>trusted communities</b>.</li>
                <li><b>Avoid links</b> from random X (Twitter) users or Telegram DMs.</li>
                <li><b>Look for audits, GitHub repos, and real backers.</b></li>
            </ul>
            <h2>⚠️ 3. Beware of Fake Accounts and Bots</h2>
            <ul>
                <li>Many scam comments and impersonators exist under legit posts.</li>
                <li>Double-check usernames and links — <b>look for subtle typos</b>.</li>
                <li><b>Never trust DMs</b> offering "airdrops" or "early access".</li>
            </ul>
            <h2>🧾 4. Audit the Smart Contract or Wait</h2>
            <ul>
                <li>Don’t rush to sign random transactions.</li>
                <li>Use tools like <b>Etherscan</b>, <b>DeBank</b>, or <b>Rabby Wallet</b> to inspect them.</li>
                <li>If a project lacks transparency or an audit, think twice.</li>
            </ul>
            <h2>🧼 5. Revoke Unused Permissions</h2>
            <ul>
                <li>Clean up your wallet permissions regularly with:</li>
                <li><a href="https://revoke.cash" target="_blank">revoke.cash</a></li>
                <li><a href="https://app.safe.global" target="_blank">Safe</a></li>
                <li>This reduces the chance of malicious token drains.</li>
            </ul>
            <h2>🔐 6. Never Share Private Keys or Seed Phrases</h2>
            <ul>
                <li><b>No legit team will ever ask</b> for your keys or phrase.</li>
                <li>Use <b>hardware wallets</b> like Ledger or Trezor for serious funds.</li>
            </ul>
            <h2>🪪 7. Watch Out for “Connect Wallet to Check Eligibility”</h2>
            <ul>
                <li>Don't connect your wallet to <b>random sites</b>.</li>
                <li>Always verify the domain and source.</li>
                <li>If in doubt, don’t click!</li>
            </ul>
            <h2>🧾 8. Use Reputable Airdrop Aggregators</h2>
            <ul>
                <li>Use vetted aggregators to spot real airdrops:</li>
                <li><a href="https://earni.fi/" target="_blank">Earnifi</a></li>
                <li><a href="https://defillama.com/airdrops" target="_blank">DeFiLlama Airdrops</a></li>
                <li>Still verify manually before connecting wallets or claiming anything.</li>
            </ul>
            <div style="background-color: #FFA500; padding: 16px; border-radius: 8px; border-left: 6px solid #FFA500; font-size: 25px; font-weight: bold; margin-top: 30px; color: white;">
                ✅ Stay tuned, stay safe, and enjoy the airdrop hunt!
            </div>
        </div>
        """,
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
            font-family: 'Space Grotesk', sans-serif;
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
        <div style="font-size:25px;font-family: 'Space Grotesk', sans-serif;">
            <p>🪂 Airdrops Monitor</p>
        </div>
        <div style="text-align: center; color: #c9ada7; font-size:25px;font-family: 'Space Grotesk', sans-serif;">
            Made with ❤️ by <a href="https://x.com/CaioFlemin2089" style="color: white; text-decoration: none;" target="_blank">@CaioFleming</a> |
            Follow for more airdrop farming strategies 🚀<br>
            Stay updated on Twitter and Discord! 📢
            <br>
            <div style="text-align: center; color: #c9ada7; font-size:18px;font-family: 'Space Grotesk', sans-serif;">
                Disclaimer: This is not financial advice. Always do your own research (DYOR)!
            </div>
        </div>
        <div style="text-align: center; color: #c9ada7; font-size:25px;font-family: 'Space Grotesk', sans-serif;">
            <p>Community: </p>
            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAAAAABXZoBIAAAA/0lEQVR4AbXPIazCMACE4d+L2qoZFEGSIGcRc/gJJB5XMzGJmK9EN0HMi+qaibkKVF1txdQe4g0YzPK5yyWXHL9TaPNQ89LojH87N1rbJcXkMF4Fk31UMrf34hm14KUeoQxGArALHTMuQD2cAWQfJXOpgTbksGr9ng8qluShJTPhyCdx63POg7rEim95ZyR68I1ggQpnCEGwyPicw6hZtPEGmnhkycqOio1zm6XuFtyw5XDXfGvuau0dXHzJp8pfBPuhIXO9ZK5ILUCdSvLYMpc6ASBtl3EaC97I4KaFaOCaBE9Zn5jUsVqR2vcTJZO1DdbGoZryVp94Ka/mQfE7f2T3df0WBhLDAAAAAElFTkSuQmCC" width="24" height="24" style="border-radius: 50%;">
            <a href="https://twitter.com/" target="_blank">Twitter</a>
            <p><a href="https://discordbot.streamlit.app/" target="_blank">🤖 Discord Bot</a></p>
        </div>
    </div>
""", unsafe_allow_html=True)

#438.153.573.297.839
#12.606.232.983

