import streamlit as st
import pandas as pd

# --- Configurações da Página ---
#st.set_page_config(page_title="Pendle Airdrop Farm", layout="wide")

# Configuração da página (sempre primeiro!)
st.set_page_config(
    page_title="Fleming Airdrop Dashboard",
    page_icon="🌐",
    layout="wide"
)

# --- Estilização Customizada ---
st.markdown("""
    <style>
        .header {
            background-color: #1c1c1c;
            padding: 1rem;
            text-align: center;
            color: white;
            font-size: 30px;
            font-weight: bold;
        }
        .footer {
            background-color: #1c1c1c;
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
st.markdown('<div class="header"> YT FARM ESTRATEGY </div>', unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("Fleming Airdrops")
st.sidebar.markdown("<h3 style='font-size: 20px;'>Options:</h3>", unsafe_allow_html=True)
opcao = st.sidebar.radio("", ["Farm with YT", "Farm with Looping", "Comparative Table"])

st.markdown("\n\n")
st.sidebar.markdown("---")
# --- Novo Quadro de Inputs ---
st.sidebar.markdown("<h3 style='font-size: 20px;'>Parameters to ROI Estimation</h3>", unsafe_allow_html=True)
with st.sidebar.expander("", expanded=True):
    invested = st.number_input("Choose the Value to Invest: $", min_value=0.0, value=1000.0, step=100.0)
    tsp = st.number_input("Expected Token Total Supply:", min_value=0, value=100_000_000)
    drop = st.number_input("Expected Percentual to Protocol Airdrop:", min_value=0.0, max_value=100.0, value=5.0)
    fdv = st.number_input("Expected FDV in TGE: $", min_value=0.0, value=50_000_000.0)

    st.markdown("---")
    Level_l_date = st.date_input("Expected Level TGE Date:")
    Open_l_date = st.date_input("Expected OpenEden TGE Date:")
    expected_fragmetric_tge_date = st.date_input("Expected Fragmetric TGE Date:")
    expected_kyros_tge_date = st.date_input("Expected Kyros TGE Date:")

# --- Dados dos Protocolos ---
protocolos = {
    "Level": {
        "Imagem": r"C:\Users\0335372\Documents\app_streamlit\Level.jpg",
        "Link": "<a href='https://app.level.money/farm?referralCode=pwlblh' target='_blank'>🔗 More info</a>",
        "TVL": "$100M",
        "Expected ROI": "12%",
        "YT Multiplier": "1.5x",
        "Boost": "1.2x",
        "Expiry": "25/06/2025",
        "Rating": "⭐⭐⭐⭐⭐",
        "Total Points Farmed": "8,320 XP",
        "Last Update": "24/04/2025",
        "Pendle YT-cUSDO": "10,000",
        "Pendle YT-cUSDO APY": "18.5%",
        "Time Until Expiration": "61 days",
        "YT Multiplier": "1.5x",
        "Referral Boost": "1.2x",
        "Equivalent YT-cUSDO Received": "9,860",
        "Daily Points Farmed": "132 XP",
        "Total Points Farmed in YT": "8,120 XP",
        "Top 100 Concentration": "72.5",
        "Farmed Yield in YT": "$140",
        "Mean Daily Points": "172 XP",
        "Estimated Points in TGE": "10,480 XP",
        "Points per Token": "1,000",
        "Estimated Token Price": "$1.25",
        "Estimated Tokens Airdrop": "10.48",
        "Estimated Airdrop Value": "$13.10",
        "Profit": "$5.10"    
    },
    "OpenEden": {
        "Imagem": r"C:\Users\0335372\Documents\app_streamlit\open.jpg",
        "Link": "<a href='https://portal.openeden.com/bills-campaign?refCode=1WgbBka17k' target='_blank'>🔗 More info</a>",
        "TVL": "$80M",
        "Expected ROI": "10%",
        "YT Multiplier": "1.3x",
        "Boost": "1.1x",
        "Expiry": "25/06/2025",
        "Rating": "⭐⭐⭐⭐☆",
        "Total Points Farmed": "8,320 XP",
        "Last Update": "24/04/2025",
        "Pendle YT-cUSDO": "10,000",
        "Pendle YT-cUSDO APY": "18.5%",
        "Time Until Expiration": "61 days",
        "YT Multiplier": "1.5x",
        "Referral Boost": "1.2x",
        "Equivalent YT-cUSDO Received": "9,860",
        "Daily Points Farmed": "132 XP",
        "Total Points Farmed in YT": "8,120 XP",
        "Top 100 Concentration": "72.5",
        "Farmed Yield in YT": "$140",
        "Mean Daily Points": "172 XP",
        "Estimated Points in TGE": "10,480 XP",
        "Points per Token": "1,000",
        "Estimated Token Price": "$1.25",
        "Estimated Tokens Airdrop": "10.48",
        "Estimated Airdrop Value": "$13.10",
        "Profit": "$5.10"         
    },
    "Fragmetric": {
        "Imagem": r"C:\Users\0335372\Documents\app_streamlit\frag.jpg",
        "Link": "<a href='https://app.fragmetric.xyz/referral?ref=77XL68' target='_blank'>🔗 More info</a>",
        "TVL": "$60M",
        "Expected ROI": "9%",
        "YT Multiplier": "1.2x",
        "Boost": "1.0x",
        "Expiry": "25/06/2025",
        "Rating": "⭐⭐⭐⭐⭐",
        "Total Points Farmed": "8,320 XP",
        "Last Update": "24/04/2025",
        "Pendle YT-cUSDO": "10,000",
        "Pendle YT-cUSDO APY": "18.5%",
        "Time Until Expiration": "61 days",
        "YT Multiplier": "1.5x",
        "Referral Boost": "1.2x",
        "Equivalent YT-cUSDO Received": "9,860",
        "Daily Points Farmed": "132 XP",
        "Total Points Farmed in YT": "8,120 XP",
        "Top 100 Concentration": "72.5",
        "Farmed Yield in YT": "$140",
        "Mean Daily Points": "172 XP",
        "Estimated Points in TGE": "10,480 XP",
        "Points per Token": "1,000",
        "Estimated Token Price": "$1.25",
        "Estimated Tokens Airdrop": "10.48",
        "Estimated Airdrop Value": "$13.10",
        "Profit": "$5.10"        
    },
    "Kyros": {
        "Imagem": r"C:\Users\0335372\Documents\app_streamlit\kyros.jpg",
        "Link": "<a href='https://boost.kyros.fi/?ref=nq3orn' target='_blank'>🔗 More info</a>",
        "TVL": "$120M",
        "Expected ROI": "14%",
        "YT Multiplier": "1.6x",
        "Boost": "1.3x",
        "Expiry": "25/06/2025",
        "Rating": "⭐⭐☆☆☆",
        "Total Points Farmed": "8,320 XP",
        "Last Update": "24/04/2025",
        "Pendle YT-cUSDO": "10,000",
        "Pendle YT-cUSDO APY": "18.5%",
        "Time Until Expiration": "61 days",
        "YT Multiplier": "1.5x",
        "Referral Boost": "1.2x",
        "Equivalent YT-cUSDO Received": "9,860",
        "Daily Points Farmed": "132 XP",
        "Total Points Farmed in YT": "8,120 XP",
        "Top 100 Concentration": "72.5",
        "Farmed Yield in YT": "$140",
        "Mean Daily Points": "172 XP",
        "Estimated Points in TGE": "10,480 XP",
        "Points per Token": "1,000",
        "Estimated Token Price": "$1.25",
        "Estimated Tokens Airdrop": "10.48",
        "Estimated Airdrop Value": "$13.10",
        "Profit": "$5.10"     
    }
}

# --- Estado de seleção ---
if "protocolo_selecionado" not in st.session_state:
    st.session_state.protocolo_selecionado = None

# --- Conteúdo Principal ---
st.title(opcao)

if opcao == "Farm with YT":
    if st.session_state.protocolo_selecionado:
        # Mostrar detalhes do protocolo selecionado
        p = st.session_state.protocolo_selecionado
        st.image(protocolos[p]["Imagem"], width=200)
        st.header(f"Detalhes de {p}")
        st.markdown(f"<p style='font-size:22px;'> Protocol: {p}  - {protocolos[p]['Link']}</p>", unsafe_allow_html=True)
        st.markdown(f"**TVL:** {protocolos[p]['TVL']}")
        st.markdown(f"**Total Points Farmed:** {protocolos[p]['Total Points Farmed']} XP")
        st.markdown(f"**Last Update:** {protocolos[p]['Last Update']}")
        st.markdown(f"**Pendle YT-cUSDO:** {protocolos[p]['Pendle YT-cUSDO']}")
        st.markdown(f"**Pendle YT-cUSDO APY:** {protocolos[p]['Pendle YT-cUSDO APY']}")
        st.markdown(f"**Time Until YT-cUSDO Expiration:** {protocolos[p]['Time Until Expiration']}")
        st.markdown(f"**Protocol YT Multiplier:** {protocolos[p]['YT Multiplier']}")
        st.markdown(f"**Protocol Referral Boost:** {protocolos[p]['Referral Boost']}")
        st.markdown(f"**Equivalent YT-cUSDO Received:** {protocolos[p]['Equivalent YT-cUSDO Received']}")
        st.markdown(f"**Daily Points Farmed:** {protocolos[p]['Daily Points Farmed']} XP")
        st.markdown(f"**Total Points Farmed in YT Expiration:** {protocolos[p]['Total Points Farmed in YT']} XP")
        st.markdown(f"**Top 100 Points Percentual Concentration:** {protocolos[p]['Top 100 Concentration']} %")
        st.markdown(f"**Farmed Yield in YT Expiration:** {protocolos[p]['Farmed Yield in YT']}")
        st.markdown(f"**Mean Daily Points (x1.30):** {protocolos[p]['Mean Daily Points']} XP")
        st.markdown(f"**Estimated Total Points in TGE:** {protocolos[p]['Estimated Points in TGE']} XP")
        st.markdown(f"**Points to Receive 1 OpenEden Token:** {protocolos[p]['Points per Token']}")
        st.markdown(f"**Estimated Token Price:** {protocolos[p]['Estimated Token Price']}")
        st.markdown(f"**Estimated Tokens Airdrop:** {protocolos[p]['Estimated Tokens Airdrop']}")
        st.markdown(f"**Estimated Airdrop Value:** {protocolos[p]['Estimated Airdrop Value']}")
        st.markdown(f"**Profit:** {protocolos[p]['Profit']}")
        st.markdown(f"**Expected ROI:** {protocolos[p]['Expected ROI']}")

        if st.button("🔙 Voltar"):
            st.session_state.protocolo_selecionado = None

    else:
        st.markdown("<h3 style='text-align: center;'></h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        cols = [col1, col2, col3]
        i = 0

        for p in protocolos:#<img src="{protocolos[p]['Imagem']}" width="200"/>
            with cols[i % 3]:
                col_left, col_center, col_right = st.columns([1, 2, 1])
                with col_center:
                    st.image(protocolos[p]['Imagem'], width=600) 
                st.markdown(f"""
                    <div style='text-align: center; font-size: 24px;'>
                        <p>TVL: {protocolos[p]['TVL']}</p>
                        <p>Expected ROI: {protocolos[p]['Expected ROI']}</p>
                        <p>YT Multiplier: {protocolos[p]['YT Multiplier']}</p>
                        <p>Boost: {protocolos[p]['Boost']}</p>
                        <p>{protocolos[p]['Expiry']}</p>
                        <p>{protocolos[p]['Rating']}</p>
                        <p></p>
                    </div>
                """, unsafe_allow_html=True)
                bcol1, bcol2 = st.columns([2, 2.6])
                with bcol2:
                    if st.button(f"View Details", key=p):
                        st.session_state.protocolo_selecionado = p
            i += 1

elif opcao == "Farm with Looping":
    st.info("🚧 Em breve: Estratégias de looping de YT.")

elif opcao == "Comparative Table":
    df = pd.DataFrame({
        "Protocolo": protocolos.keys(),
        "TVL": [protocolos[p]["TVL"] for p in protocolos],
        "Expected ROI": [protocolos[p]["Expected ROI"] for p in protocolos],
        "YT-Multiplier": [protocolos[p]["YT Multiplier"] for p in protocolos],
        "Protocol Boost": [protocolos[p]["Boost"] for p in protocolos],
        "Expiry": [protocolos[p]["Expiry"] for p in protocolos],
        "Rating": [protocolos[p]["Rating"] for p in protocolos],
    })
    st.dataframe(df, use_container_width=True)

# --- Footer ---
st.markdown("""
    <style>
        .footer {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;  /* 3 colunas */
            grid-gap: 20px;
            background-color: #333;
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
            <p>🌐 Fleming Airdrop</p>
        </div>
        <div> 
            <p>Community: </p>
            <p><a href="https://twitter.com/" target="_blank">Twitter</a></p>
            <p><a href="https://telegram.org/" target="_blank">Telegram</a></p>
            <p><a href="https://github.com/" target="_blank">Github</a></p>
        </div>
        <div>
            <p><strong>Advice:</strong></p>
            <p>Check out the latest airdrops and farming strategies to maximize your rewards.</p>
            <p>Stay updated on Twitter and Discord of each protocol!</p>
        </div>
    </div>
""", unsafe_allow_html=True)

438.153.573.297.839
12.606.232.983