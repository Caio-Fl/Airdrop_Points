import streamlit as st

exchanges = [
    "backpack",
    "binance",
    "mexc",
    "gate.io",
    "extended",
    "paradex",
    "pacifica",
    "hyperliquid",
    "lighter",
    "nado",
]

logos = {
    "backpack": "https://pbs.twimg.com/profile_images/1957829985143791616/sA2YoWNq_400x400.jpg",
    "binance": "https://pbs.twimg.com/profile_images/1940131561103347712/f5y2qENu_400x400.jpg",
    "mexc": "https://pbs.twimg.com/profile_images/2016433568231391236/Zfdec3Us_400x400.jpg",
    "gate.io": "logos/gate.png",
    "extended": "logos/extended.png",
    "paradex": "logos/paradex.png",
    "pacifica": "logos/pacifica.png",
    "hyperliquid": "logos/hyperliquid.png",
    "lighter": "logos/lighter.png",
    "nado": "logos/nado.png",
}

col1, col2 = st.columns([4,1])

with col1:
    exchange = st.selectbox(
        "Exchange:",
        exchanges,
        format_func=lambda x: x.replace(".", ". ").title().replace(". ", ".")
    )

with col2:
    st.markdown(
        f"""
        <div style="margin-top: 25px;">
            <img src="{logos[exchange]}" width="45">
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("Valor retornado para o código 👉", exchange)