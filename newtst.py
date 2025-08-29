import streamlit as st
import requests
import cloudscraper
import streamlit.components.v1 as components

st.set_page_config(page_title="Farm Dashboard", layout="wide")
st.title("🌍 Multi-Protocol Farm Dashboard")

# -------------------------
# 🔹 HELPER
# -------------------------
def safe_request(url, params=None, payload=None, use_scraper=False, method="GET"):
    try:
        scraper = cloudscraper.create_scraper() if use_scraper else requests
        if method == "GET":
            res = scraper.get(url, params=params)
        else:  # POST
            res = scraper.post(url, json=payload)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Erro ao acessar {url}: {e}")
    return None

# -------------------------
# 🔹 FETCH FUNCTIONS
# -------------------------
def get_ethena(wallet: str):
    url = f"https://app.ethena.fi/api/referral/get-referree?address={wallet}"
    data = safe_request(url)
    if data and data.get("queryWallet"):
        d = data["queryWallet"][0]
        try:
            return {
                "points": d.get("accumulatedTotalShardsEarned", 0),
                "referrals": d.get("accumulatedReferralsShards", 0),
                "extra": f"<br>💎 Pendle: {d.get('accumulatedPendleShards',0):,.2f} / 🌱 Restaking: {d.get('accumulatedRestakingShards', 0):,.0f}</br> <br> 🚀 Boost: {d.get('accumulatedBoostShards', 0):,.0f} / 🌐 L2: {d.get('accumulatedL2Shards', 0):,.0f} </br>",
                "raw": data
            }
        except:
            return None
    return None

def get_ethereal(wallet: str):
    url = f"https://deposit-api.ethereal.trade/v1/account/{wallet}"
    data = safe_request(url)
    if data:
        try:
            pts = int(data["accounts"][0].get("points", 0)) / 1e18 if data.get("accounts") else 0
            s0_pts = int(data["accountsS0"][0].get("points",0)) / 1e18 if data.get("accountsS0") else 0
            return {
                "points": pts,
                "extra": f"<br>🔹 S0 Points: {s0_pts:,.2f}</br> <br> </br>",
                "rank": data.get("rank", "N/A"),
                "raw": data
            }
        except:
            return None
    return None

def get_hylo(wallet: str):
    url = "https://hylo.so/api/user-points"
    data = safe_request(url, params={"address": wallet}, use_scraper=True)
    if data:
        return {
            "points": data.get("totalPoints", 0),
            "rank": data.get("globalRank", "N/A"),
            "extra": f"<br>👥 Referral Points: {data.get('referralPoints',0):,.2f}</br> <br> </br>",
            "raw": data
        }
    return None

def get_level(wallet: str):
    url = f"https://api.level.money/v1/xp/balances/leaderboard?page=1&take=1&referral=false&addresses={wallet}"
    data = safe_request(url)
    if data and data.get("leaderboard"):
        lb = data["leaderboard"][0]["balance"]
        return {
            "points": int(lb.get("accrued", 0)),
            "rank": data.get("rank", "N/A"),
            "extra": f"<br>👥 Referral Points: {int(lb.get('fromReferrals',0)):,.2f}</br>  <br> </br>",
            "raw": data
        }
    return None

def get_noon(wallet: str):
    url = f"https://back.noon.capital/api/v1/points/{wallet}"
    data = safe_request(url, use_scraper=True)
    if data:
        try:
            total = int(data["totalPoints"]) / 1e17
            last24h = int(data["last24HoursPoints"]) / 1e17
            return {
                "points": total,
                "extra": f"<br>⏱ Last24h: {last24h:,.2f}</br> <br> </br>",
                "raw": data
            }
        except:
            return None
    return None

def get_plume(wallet: str):
    url = f"https://portal-api.plume.org/api/v1/stats/pp-totals?walletAddress={wallet}"
    data = safe_request(url)
    if data and "data" in data and data["data"].get("ppScores"):
        pp = data["data"]["ppScores"]
        return {
            "points": pp["activeXp"].get("totalXp",0),
            "extra": f"<br>👥 Referral Points: {pp['activeXp'].get('referralBonusXp',0):,.2f}</br>",
            "raw": data
        }
    return None

def get_yieldfi_points(wallet: str):
    url = f"https://ctrl.yield.fi/u/points/{wallet}"
    data = safe_request(url, use_scraper=True)
    if data:
        return {
            "points": data.get("totalPoints",0),
            "extra": f"<br></br> <br></br>",
            "raw": data
        }
    return None

def get_kyros(wallet: str):
    url = f"https://points-api.kyros.fi/score?wallet={wallet}"
    data = safe_request(url)
    if data:
        return {
            "points": data.get("points",0),
            "rank": data.get("rank","N/A"),
            "extra": f"<br>👥 Referral Points: {data.get('referralPoints',0):,.2f}</br> <br> </br>",
            "raw": data
        }
    return None

def get_triad(wallet: str):
    url = f"https://beta.triadfi.co/user/{wallet}/rank"
    data = safe_request(url, use_scraper=True)
    if data:
        return {
            "points": data.get("points",0),
            "rank": data.get("rank","N/A"),
            "extra": f"<br>TRD Staked: {data.get('trdStaked',0):,.2f}</br> <br> </br>",
            "raw": data
        }
    return None

def get_kinetiq(wallet: str):
    url = f"https://kinetiq.xyz/api/points/{wallet}?chainId=999"
    data = safe_request(url)
    if data:
        return {
            "points": data.get("points",0),
            "extra": f"<br>⭐ Tier: {data.get('tier','N/A')}</br> <br> </br>",
            "raw": data
        }
    return None

def get_hyperbeat(wallet: str):
    url = f"https://app.hyperbeat.org/api/hyperfolio/points?address={wallet}"
    data = safe_request(url)
    if data and "points" in data:
        total = sum(float(p.get("balance",0)) for p in data["points"])
        return {
            "points": total,
            "extra": f"<br> Kittenswap: {data.get('Kittenswap', 0):,.2f} / Hyperswap: {data.get('Hyperswap', 0):,.2f} / Hyperlend: {data.get('Hyperlend', 0):,.2f}</br> <br> Felix: {data.get('Felix', 0):,.2f} / Upshift: {data.get('Upshift', 0):,.2f} / Hyperdrive: {data.get('Hyperdrive', 0):,.2f}</br>",
            "raw": data
        }
    return None

def get_prjx(wallet: str):
    url = f"https://api.prjx.com/scorecard/impersonate/{wallet}?format=json"
    data = safe_request(url)
    if data and data.get("stats"):
        return {
            "points": data["stats"].get("totalPoints",0),
            "rank": data["stats"].get("rank","N/A"),
            "extra": f"<br>👥 Referrals Points: {data['stats'].get('totalReferrals',0):,.2f}</br> <br> </br>",
            "raw": data
        }
    return None

def get_ratex(wallet: str):
    url = "https://api.rate-x.io/"
    payload = {"serverName":"AdminSvr","method":"queryRatexPoints","content":{"user_id":wallet}}
    data = safe_request(url, method="POST", payload=payload)
    if data and data.get("code")==0 and data.get("data"):
        item = data["data"][0]
        return {
            "points": float(item.get("total_points",0)),
            "extra": f"<br>LP: {item.get('lp_points',0):,.2f}, Trade: {item.get('trade_points',0):,.2f}</br> <br> </br>",
            "rank": item.get("ranking","N/A"),
            "raw": item
        }
    return None

def get_lombard(wallet: str):
    url = f"https://mainnet.prod.lombard.finance/api/v1/referral-system/season-1/points/{wallet}"
    data = safe_request(url)
    if data:
        return {
            "points": data.get("total",0),
            "extra": f"<br>🎖️ Badges Points: {data.get('badges',0)} / 💼 Holding Points: {data.get('holding_points'):,.2f}</br> <br> </br>",
            "raw": data
        }
    return None


# -------------------------
# 🔹 PROTOCOLS CONFIG
# -------------------------
protocols = [
    {
        "name": "Ethena",
        "site": "app.ethena.fi/join/yp9pg",
        "image": "https://pbs.twimg.com/profile_images/1684292904599126016/f0ChONgU_400x400.png",
        "fetch": get_ethena,
    },
    {
        "name": "Ethereal",
        "site": "https://deposit.ethereal.trade/points?ref=KVHDUP",
        "image": "https://pbs.twimg.com/profile_images/1949907904816988160/wPykUsI0_400x400.jpg",
        "fetch": get_ethereal,
    },
    {
        "name": "Level",
        "site": "https://app.level.money/farm?referralCode=pwlblh",
        "image": "https://pbs.twimg.com/profile_images/1811061996172840960/wy0N3CoS_400x400.jpg",
        "fetch": get_level,
    },
    {
        "name": "Noon",
        "site": "https://app.noon.capital/get?referralCode=f351689c-2391-4d2b-a963-d24a5530753a",
        "image": "https://pbs.twimg.com/profile_images/1927790098906497025/Ze-SQcgt_400x400.jpg",
        "fetch": get_noon,
    },
    {
        "name": "Plume",
        "site": "https://portal.plume.org/?referrer=MagnoliaBustlingAnt788",
        "image": "https://pbs.twimg.com/profile_images/1949681985149956096/ttJazkDy_400x400.jpg",
        "fetch": get_plume,
    },
    {
        "name": "YieldFi",
        "site": "https://yield.fi/yusd?referral=E4TAZUVU",
        "image": "https://pbs.twimg.com/profile_images/1922944632180310016/tN3q4S8G_400x400.jpg",
        "fetch": get_yieldfi_points,
    },
    {
        "name": "Hylo",
        "site": "https://hylo.so/leverage?ref=E27KDV",
        "image": "https://pbs.twimg.com/profile_images/1939067421895081987/73ljl6zx_400x400.png",
        "fetch": get_hylo,
    },
    {
        "name": "Kyros",
        "site": "https://boost.kyros.fi/?ref=nq3orn",
        "image": "https://pbs.twimg.com/profile_images/1847426788252590080/-Tb-I1Yl_400x400.jpg",
        "fetch": get_kyros,
    },
    {
        "name": "Triad",
        "site": "https://triadfi.co/?ref=Caio Fleming",
        "image": "https://pbs.twimg.com/profile_images/1955263071758225408/TqPBIm8I_400x400.jpg",
        "fetch": get_triad,
    },
    {
        "name": "RateX",
        "site": "https://app.rate-x.io/referral?ref=H9GnKZON",
        "image": "https://pbs.twimg.com/profile_images/1790703675700355072/wUBLpPIS_400x400.jpg",
        "fetch": get_ratex,
    },
    {
        "name": "Kinetiq",
        "site": "https://kinetiq.xyz",
        "image": "https://pbs.twimg.com/profile_images/1880410606093647872/qazlkvcq_400x400.jpg",
        "fetch": get_kinetiq,
    },
    {
        "name": "Hyperbeat",
        "site": "https://app.hyperbeat.org/earn?referral=F56B5BD8",
        "image": "https://pbs.twimg.com/profile_images/1879158343194796032/ftN7FT3s_400x400.jpg",
        "fetch": get_hyperbeat,
    },
    {
        "name": "Project X",
        "site": "https://www.prjx.com/@Fleming",
        "image": "https://pbs.twimg.com/profile_images/1922089219737911296/1miGhDTB_400x400.jpg",
        "fetch": get_prjx,
    },
    {
        "name": "Lombard",
        "site": "https://www.lombard.finance/app/?referrer=fgx6lb",
        "image": "https://pbs.twimg.com/profile_images/1945866084202004480/sF1I4lkP_400x400.jpg",
        "fetch": get_lombard,
    }
]


# -------------------------
# 🔹 INPUT
# -------------------------
wallets_input = st.text_input(
    "Digite uma ou mais carteiras (0x...), separadas por vírgula",
    value="0x2A78c88C4012544D11E41736505B8D67abBA0532"
)
# -------------------------
# 🔹 CSS
# -------------------------
st.markdown("""
<style>
.container-externa {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 15px;
}
.container-block {
    background: #1E1F25;
    border-radius: 15px;
    padding: 20px;
    max-width: 380px;   /* <-- limita para não estourar */
    color: white;
    text-align: center;
    border: 1px solid rgba(0,255,255,0.2);
    box-shadow: 0 0 15px rgba(0,255,255,0.4);
    transition: transform 0.2s;
}
.container-block:hover {
    transform: scale(1.05);
}
.container-block img {
    border-radius: 50%;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 🔹 RENDER COM LAYOUT NEON
# -------------------------
if wallets_input:
    wallets = [w.strip() for w in wallets_input.split(",") if w.strip()]
    tabs = st.tabs(wallets)  # cria uma aba para cada wallet

    for i, wallet in enumerate(wallets):
        with tabs[i]:

            blocks_html = ""
            for proto in protocols:
                data = proto["fetch"](wallet)
                if not data or data.get("points") in [None, 0, "N/A"]:
                    continue

                points = f"{data.get('points', 0):,.2f}"
                rank = data.get("rank", "N/A")
                extra = f"<p>{data.get('extra', '')}</p>"

                blocks_html += f"""
                <div class="container-block" style="overflow: hidden;">
                    <div class="header-wrapper">
                        <img src="{proto['image']}" width="50" height="50" style="border-radius: 50%;">
                        <div>
                            <strong style="text-shadow: 0 0 4px #14ffe9, 0 0 4px #14ffe9;">{proto['name']}</strong>
                        </div>
                    </div>
                    <div class="footer-wrapper">
                        <p><strong>🌟 Points: {points}</strong></p>
                        <p><strong>🏆 Rank: {rank}</strong></p>
                        <div style="font-size: 12px;">{extra}</div>
                        <p><strong>🌐 Site: <a href="{proto['site']}" style="color: lightblue;" target="_blank">Visit Protocol</a></strong></p>
                    </div>
                </div>
                """

            # HTML completo com o mesmo CSS neon
            full_html = f"""
            <style>
            @keyframes neonBorder {{
                0%   {{ background-position: 0% 50%; }}
                50%  {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            .container-externa {{
                border-radius: 12px;
                padding: 25px;
                margin-top: 30px;
                gap: 0px;
                display: flex;
                flex-wrap: wrap;
                justify-content: left;
                font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
                font-size: 22px;
                color: white;
                margin: 0px 0;
                align-items: center;
                justify-content: center;
                overflow: hidden;
                scrollbar-width: none;
            }}
            .container-externa::-webkit-scrollbar {{
                display: none; /* Chrome/Safari */
            }}
            .container-block {{
                width: 500px;
                flex-shrink: 0; 
                margin: 10px;
            }}
            .header-wrapper {{
                width: 330px;
                padding: 30px;
                margin-top: 10px;
                margin-right: 15px;
                margin-left: 12px;
                border-top: 1px solid rgba(48, 240, 192, 0.2);
                border-bottom: 1px solid #00e0ff;
                border-top-left-radius: 40px;
                border-top-right-radius: 10px;  /* 👈 maior */
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
                display: flex;
                align-items: center;
                gap: 30px;
                background: #1E1F25;
                box-shadow: 0 0 20px rgba(0,255,150,0.3);
                transition: transform 0.3s ease;
                font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
                z-index: 1;
                overflow: hidden;
                align-items: center;
                justify-content: center;
            }}
            .header-wrapper:hover {{
                border: 1px solid #39ff14; /* Verde neon */
                border-top-left-radius: 40px;
                border-top-right-radius: 10px; 
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
                box-shadow: 0 0 4px #39ff14, 0 0 8px #39ff14; /* Brilho neon suave */
                background: #262b33;
            }}
            .header-wrapper:hover::before {{
                content: "";
                position: absolute;
                top: -3px;
                left: -3px;
                right: -3px;
                bottom: -3px;
                border-radius: 14px;
                z-index: -1;
                animation: neonBorder 6s ease infinite;
                -webkit-mask:
                    linear-gradient(#fff 0 0) content-box,
                    linear-gradient(#fff 0 0);
                -webkit-mask-composite: xor;
                mask-composite: exclude;
            }}
            .header-wrapper a {{
                color: lightblue;
                text-decoration: none;
            }}
            .footer-wrapper {{
                width: 330px;
                padding: 30px;
                margin-top: 6px;
                margin-bottom: 30px;
                margin-right: 15px;
                margin-left: 12px;
                border-top: 1px solid #00e0ff;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;  /* 👈 maior */
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 40px;
                display: block;
                align-items: center;
                gap: 30px;
                background: #1E1F25;
                box-shadow: 0 0 20px rgba(0,255,150,0.5);
                transition: transform 0.3s ease;
                font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
                z-index: 1;
                overflow: hidden;
                align-items: center;
                justify-content: center;
                font-size:20px;
            }}
            .footer-wrapper:hover {{
                border: 1px solid #39ff14; /* Verde neon */
                border-top-left-radius: 5px;
                border-top-right-radius: 5px; 
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 40px;
                box-shadow: 0 0 4px #39ff14, 0 0 8px #39ff14; /* Brilho neon suave */
                background: #262b33;
            }}
            .footer-link {{
                text-decoration: none;
                margin: 0;
                width: 100%;
                color: inherit;
            }}
            .footer-link:hover {{
                color: inherit;
            }}
            </style>

            <div class="container-externa">
                {blocks_html}
            </div>
            """

            components.html(full_html, height=1900, width=None, scrolling=False)