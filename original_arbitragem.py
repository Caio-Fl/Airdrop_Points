elif st.session_state.pagina == "📊 Funding Rate Arbitrage":

    import requests
    import streamlit.components.v1 as components

    API_URL = "https://www.cryptoexchange.sh/api/funding-arb"

    # ------------------------------
    # LINKS DOS PROTOCOLOS
    # ------------------------------
    EXCHANGE_LINKS = {
        "VARIATIONAL": "https://omni.variational.io/",
        "PACIFICA": "https://app.pacifica.fi?referral=PacificaRef",
        "OSTIUM": "https://app.ostium.com/trade?from=SPX&to=USD&ref=EIETH",
        "HYPERLIQUID": "https://app.hyperliquid.xyz/join/HYPER15",
        "EXTENDED": "https://app.extended.exchange/join/EXT3NDED15",
        "LIGHTER": "https://app.lighter.xyz/?referral=LIGHTER15",
    }

    def link_exchange(name: str):
        if not name:
            return "-"
        key = name.upper()
        url = EXCHANGE_LINKS.get(key)
        if url:
            return f'<a href="{url}" target="_blank" style="color:#3cff9e; text-decoration:none; font-weight:600;">{key}</a>'
        return key

    # ------------------------------
    # Request
    # ------------------------------
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        json_data = response.json()
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        st.stop()

    markets = json_data.get("data", [])
    rwa_markets = json_data.get("rwaTopOpportunities", [])

    # ------------------------------
    # Sidebar filtros
    # ------------------------------
    st.sidebar.markdown("## ⚙️ Funding Arbitrage Filters")

    min_spread = st.sidebar.slider(
        "Spread mínimo (%)",
        min_value=0.0,
        max_value=2.0,
        value=0.05,
        step=0.01
    )

    top_n = st.sidebar.slider(
        "Top oportunidades destacadas",
        min_value=3,
        max_value=20,
        value=10,
        step=1
    )

    # ------------------------------
    # Header
    # ------------------------------
    st.markdown(
        """
        <style>
            .airdrop-box {
                position: relative;
                z-index: 1;
                border-radius: 12px;
                padding: 25px;
                margin: 20px 0;
                background: #111827;
                display: flex;
                flex-direction: column;
                gap: 30px;
                font-size: 20px;
                color: white;
                font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
                overflow-wrap: break-word;
                word-wrap: break-word;
                white-space: normal;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
            }

            /* Borda neon com gradiente animado */
            .airdrop-box::before {
                content: "";
                position: absolute;
                top: -3px;
                left: -3px;
                right: -3px;
                bottom: -3px;
                border-radius: 14px;
                z-index: -1;
                background: linear-gradient(270deg, #00F0FF, #39FF14, #00F0FF);
                background-size: 600% 600%;
                animation: neonBorder 6s ease infinite;
                padding: 3px;
                -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
                -webkit-mask-composite: xor;
                mask-composite: exclude;
            }

            /* Efeito de hover */
            .airdrop-box:hover {
                border-color: #00f0ff;
                background: #262b33;
            }

            @keyframes neonBorder {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            .airdrop-box h1 {
                font-size: 25px;
                text-align: center;
                margin-bottom: 5px;
            }

            .airdrop-box h2 {
                font-size: 25px;
                margin-top: 5px;
                margin-bottom: 5px;
                color: #00ffae;
            }

            .airdrop-box ul {
                margin-left: 20px;
                margin-bottom: 5px;
            }
        </style>

        <div class="airdrop-box">
            <h2>Funding Rate Arbitrage</h2>
            <p style="color: #8293A3;">
                Find the arbitrage opportunities by tracking the real-time funding rate differences across decentralized exchanges (updated every 5 minutes).
            </p>
            <h2>What to do?</h2>
            <ul style="color: #8293A3;">
                <li><strong>Asset selection:</strong> Choose a coin with a large funding gap (or best daily APY) between two exchanges from the ranking below.</li>
                <li><strong>Where to sell (Short):</strong> Open a short position where funding is highest and positive (you get paid).</li>
                <li><strong>Where to buy (Long):</strong> Open a long position where funding is lowest or negative (low or negative cost).</li>
                <li><strong>Balance:</strong> Use the same notional (e.g. $1,000 each side) and the same leverage (1x–3x recommended).</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------
    # Builders
    # ------------------------------
    def prepare_markets(data):
        processed = []

        for m in data:
            spread_pct = m.get("spreadPct", 0) * 100
            funding_diff = m.get("fundingDiff", 0)
            apy_diario = funding_diff * 24 * 100
            apy_anual = apy_diario * 365

            if spread_pct >= min_spread:
                m["spread_pct"] = round(spread_pct, 4)
                m["funding_diff_pct"] = round(funding_diff * 100, 5)
                m["apy_diario"] = round(apy_diario, 4)
                m["apy_anual"] = round(apy_anual, 4)
                processed.append(m)

        processed = sorted(processed, key=lambda x: x["apy_diario"], reverse=True)
        return processed

    def build_blocks(data):
        blocks_html = ""

        for idx, m in enumerate(data):
            symbol = m.get("symbol", "")
            spread_pct = m["spread_pct"]
            funding_diff = m["funding_diff_pct"]
            apy_diario = m["apy_diario"]
            apy_anual = m["apy_anual"]

            min_v = m.get("minFundingVenue", {})
            max_v = m.get("maxFundingVenue", {})

            long_name = link_exchange(min_v.get("venue", ""))
            short_name = link_exchange(max_v.get("venue", ""))

            highlight_class = "highlight-block" if idx < top_n else "protocol-block"

            venues_html = ""
            for v in m.get("venues", []):
                venues_html += f"""
                    <div style="font-size:14px; opacity:0.9; margin-top:3px;">
                        {link_exchange(v.get("venue",""))} | funding: {round(v.get("funding",0)*100,5)}% | OI: ${round(v.get("openInterestUsd",0),2):,}
                    </div>
                """

            blocks_html += f"""
                <div class="{highlight_class}">
                    <div class="header-wrapper">
                        <strong style="font-size:26px; text-shadow:0 0 6px #14ffe9;">
                            #{idx+1} — {symbol}
                        </strong>
                        <p style="margin-top:6px;">
                            📈 Funding: {funding_diff}% |💰 daily APY: <b style="color:#3cff9e;">{apy_diario}%</b>
                        </p>
                    </div>

                    <div class="footer-wrapper">
                        <p>🟢 Long: {long_name} — {round(min_v.get("funding",0)*100,5)}%</p>
                        <p>🔴 Short: {short_name} — {round(max_v.get("funding",0)*100,5)}%</p>
                        <p>⚡ Spread: {spread_pct}%</p>
                        <p>💰 Anual APY: {apy_anual}%</p>
                        <div style="margin-top:10px;">{venues_html}</div>
                    </div>
                </div>
            """

        return blocks_html

    crypto_markets = prepare_markets(markets)
    rwa_markets = prepare_markets(rwa_markets)

    # ------------------------------
    # CSS
    # ------------------------------
    block_style_css = """
    <style>
        .container-externa {
            border-radius: 12px;
            padding: 10px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
            color: white;
        }

        .protocol-block {
            width: 350px;
            border-radius: 14px;
            padding: 20px;
            margin: 12px;
            background: #121217;
            box-shadow: 0 0 16px rgba(0,255,150,0.25);
            transition: 0.3s;
        }

        .highlight-block {
            width: 350px;
            border-radius: 16px;
            padding: 22px;
            margin: 12px;
            background: linear-gradient(135deg, #0f2f23, #121217);
            box-shadow: 0 0 30px rgba(0,255,150,0.85);
            border: 1px solid rgba(80,255,180,0.6);
            transform: scale(1.03);
        }

        .header-wrapper {
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(48, 240, 192, 0.15);
        }

        .footer-wrapper {
            margin-top: 10px;
            font-size:16px;
        }
    </style>
    """

    # ------------------------------
    # Crypto section
    # ------------------------------
    st.markdown("## 🔥 Crypto Top Opportunities")

    crypto_html = f"""
        {block_style_css}
        <div class="container-externa">
            {build_blocks(crypto_markets)}
        </div>
    """

    components.html(crypto_html, height=3200, scrolling=True)

    # ------------------------------
    # RWA section
    # ------------------------------
    if rwa_markets:
        st.markdown("## 🏛 RWA Top Opportunities")

        rwa_html = f"""
            {block_style_css}
            <div class="container-externa">
                {build_blocks(rwa_markets)}
            </div>
        """

        components.html(rwa_html, height=2600, scrolling=True)