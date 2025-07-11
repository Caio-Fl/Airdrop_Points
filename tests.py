import streamlit as st

# --- CSS que aplica estilo APENAS ao container após o marcador <div id="airdrop-container">
st.markdown("""
        <style>
        [data-testid="stHorizontalBlock"] > div {
            background-color: transparent !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)

# --- Marcador identificador visual (NÃO quebra o layout, mas serve como âncora para o CSS)

st.markdown('<div class="airdrop-container">', unsafe_allow_html=True)
# --- Container isolado (este é o que recebe o estilo!)
with st.container():
    st.subheader("🧮 Fragmetric Airdrop Simulator")

    col1, col2 = st.columns(2)
    with col1:
        selected_protocol = st.selectbox("Select Protocol", ["Any", "Level", "Kyros", "Spark", "Gaib"])
        FDV = st.number_input("💰 Estimated FDV (USD)", value=100_000_000, step=1_000_000)
        airdrop_pct = st.number_input("🎯 Supply % for Airdrop", value=10, step=1)

    with col2:
        total_points = st.number_input("📊 Estimated Total Points", value=1_000_000, step=10_000)
        your_points = st.number_input("🎟️ Your Points", value=1000, step=100)
st.markdown('</div>', unsafe_allow_html=True)