import streamlit as st
from pathlib import Path
import base64

st.set_page_config(page_title="Bridge & Swap Airdrops", layout="wide")

# Updated protocols data including Sonic and Hyperlane networks
protocols_bridge_swap = {
    "EVM": [
        {"name": "Relay", "site": "https://relaychain.xyz", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1889316674383282176/ulV41xZ7_400x400.jpg"},
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
        {"name": "KyberSwap", "site": "https://kyberswap.com/swap/sonic",  "fees": "Loe", "image": "https://pbs.twimg.com/profile_images/1641706567014940672/UFuWgdxn_400x400.jpg"},    
        {"name": "SquidRouter", "site": "https://app.squidrouter.com", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1548647667135291394/W2WOtKUq_400x400.jpg"},
        {"name": "Stargate", "site": "https://stargate.finance", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1453865643053182980/s9_nNOkD_400x400.jpg"},
        {"name": "Hyperlane", "site": "https://hyperlane.xyz", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1671589406816313345/wGzRPeEf_400x400.jpg"}, 
        {"name": "Merkly", "site": "https://minter.merkly.com/hyperlane/token", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1730147960082628608/3Oz6434E_400x400.jpg"},
        {"name": "Across Protocol", "site": "https://app.across.to/bridge?", "fees": "Fair", "image": "https://pbs.twimg.com/profile_images/1886903904874512384/wnRMhfef_400x400.jpg"},
        {"name": "Rhino.fi", "site": "https://rhino.fi", "fees": "High", "image": "https://pbs.twimg.com/profile_images/1715027429989773312/WDP-gVnU_400x400.jpg"},
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
        {"name": "Relay", "site": "https://relaychain.xyz", "fees": "Low", "image": "https://pbs.twimg.com/profile_images/1889316674383282176/ulV41xZ7_400x400.jpg"},
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
        {"name": "Skip.go", "site": "https://ibcprotocol.org", "fees": "Fair", "image": "https://ibcprotocol.org/logo.png"},
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

# Style setup
st.markdown("""
    <style>
        body {background-color: #c3a9a5;}
        .title-style {
            font-size: 36px;
            font-weight: bold;
            color: #fbd46d;
            margin-bottom: 20px;
        }
        .card {
            border: 3px solid white;
            border-radius: 10px;
            padding: 10px;
            background-color: #342b44;
            color: white;
            margin: 10px;
        }
        .inner-card {
            background-color: #2c4a6b;
            padding: 10px;
            border-radius: 10px;
            margin-top: 5px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title-style'>🎉 Bridge & Swap Airdrops</h1>", unsafe_allow_html=True)

# Network selection
selected_network = st.selectbox("Select a network:", list(protocols_bridge_swap.keys()), format_func=lambda x: x.upper())

# Render selected network section
st.subheader(selected_network.upper())
cols = st.columns(3)
for idx, protocol in enumerate(protocols_bridge_swap[selected_network]):
    with cols[idx % 3]:
        st.markdown(f"""
            <div class="card">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <img src="{protocol['image']}" width="50" height="50" style="border-radius: 50%;">
                    <h4 style="margin: 0;color: #FFA500">{protocol['name']}</h4>
                </div>
                <div class="inner-card">
                    <p>🌐 Site: <a href="{protocol['site']}" style="color: lightblue;" target="_blank">Visit Protocol</a></p>
                    <p>💸 Taxas: {protocol['fees']}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
