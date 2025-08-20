import requests
import pandas as pd
import streamlit as st
import cloudscraper

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
    return data["queryWallet"][0] if data and data.get("queryWallet") else None

def get_hylo(wallet: str):
    url = "https://hylo.so/api/user-points"
    return safe_request(url, params={"address": wallet}, use_scraper=True)

def get_level(wallet: str):
    url = f"https://api.level.money/v1/xp/balances/leaderboard?page=1&take=1&referral=false&addresses={wallet}"
    data = safe_request(url)
    print(data)
    if data and data.get("leaderboard"):
        return {
            "rank": data.get("rank", "N/A"),
            "accrued": int(data["leaderboard"][0]["balance"]["accrued"]),
            "referrals": int(data["leaderboard"][0]["balance"].get("fromReferrals", 0))
        }
    return None

def get_noon(wallet: str):
    url = f"https://back.noon.capital/api/v1/points/{wallet}"
    data = safe_request(url, use_scraper=True)  # usa cloudscraper para evitar bloqueio
    if data:
        try:
            # Convertendo para float (dividindo por 10^17)
            total = int(data["totalPoints"]) / 1e17
            last_24h = int(data["last24HoursPoints"]) / 1e17
            usn_total = int(data["byChain"]["1"]["byProtocol"]["usn"]["total"]) / 1e17
            usn_last_24h = int(data["byChain"]["1"]["byProtocol"]["usn"]["last24h"]) / 1e17

            return {
                "totalPoints": total,
                "last24h": last_24h,
                "usn_total": usn_total,
                "usn_last_24h": usn_last_24h,
                "raw": data
            }
        except Exception as e:
            st.error(f"Erro ao processar dados da Noon: {e}")
            return None
    return None

def get_kyros(wallet: str):
    url = f"https://points-api.kyros.fi/score?wallet={wallet}"
    data = safe_request(url)
    if data:
        return {
            "rank": data.get("rank"),
            "points": data.get("points"),
            "holdingPoints": data.get("holdingPoints"),
            "defiPoints": data.get("defiPoints"),
            "liquidityPoints": data.get("liquidityPoints"),
            "referralPoints": data.get("referralPoints"),
            "exponentPoints": data.get("exponentPoints"),
            "rateXSolPoints": data.get("rateXSolPoints"),
            "raw": data
        }
    return None

def get_triad(wallet: str):
    url = f"https://beta.triadfi.co/user/{wallet}/rank"
    data = safe_request(url, use_scraper=True)
    if data:
        return {
            "points": data.get("points", 0),
            "rank": data.get("rank", "N/A"),
            "referralPoints": data.get("providedReferralPoints", 0),
            "trdStaked": data.get("trdStaked", 0),
            "raw": data
        }
    return None

def get_kinetiq(wallet: str):
    url = f"https://kinetiq.xyz/api/points/{wallet}?chainId=999"
    return safe_request(url)

def get_hyperbeat(wallet: str):
    try:
        url = f"https://app.hyperbeat.org/api/hyperfolio/points?address={wallet}"
        data = safe_request(url)
        if data and "points" in data:
            total = sum(float(item.get("balance", 0)) for item in data["points"])
            return {"total": total, "details": data["points"]}
        return None
    except:
        return None

def get_perena(wallet: str):
    url = "https://api.perena.org/api/rewards"
    payload = {"publicKey": wallet}
    data = safe_request(url, method="POST", payload=payload)
    if data:
        season0 = data.get("season0RewardsData", {})
        preseason1 = data.get("preseason1RewardsData", {})

        total = (season0.get("totalPoints", 0) or 0) + (preseason1.get("totalPoints", 0) or 0)

        return {
            "total": total,
            "season0": season0,
            "preseason1": preseason1
        }
    return None

def get_ratex(wallet: str):
    url = "https://api.rate-x.io/"
    payload = {
        "serverName": "AdminSvr",
        "method": "queryRatexPoints",
        "content": {
            "user_id": wallet  # aqui passa a carteira / ID de usuário
        }
    }
    data = safe_request(url, method="POST", payload=payload)
    if data and data.get("code") == 0 and data.get("data"):
        item = data["data"][0]
        return {
            "total_points": float(item.get("total_points", 0)),
            "lp_points": float(item.get("lp_points", 0)),
            "trade_points": float(item.get("trade_points", 0)),
            "kol_points": float(item.get("kol_points", 0)),
            "earn_points": float(item.get("earn_points", 0)),
            "boost": float(item.get("boost", 0)),
            "ranking": item.get("ranking", "N/A"),
            "gear_text": item.get("gear_text", ""),
            "raw": item
        }
    return None

def get_ranger(wallet: str):
    url = "https://www.app.ranger.finance/api/referral/get-referrer"
    payload = {"publicKey": wallet}
    data = safe_request(url, method="POST", payload=payload)
    if data:
        return {
            "total_rewards": data.get("total_rewards", 0),
            "total_volume": data.get("total_volume", 0),
            "spot_volume": data.get("spot_volume", 0),
            "perps_volume": data.get("perps_volume", 0),
            "spot_points": data.get("spot_points", 0),
            "perps_points": data.get("perps_points", 0),
            "total_points": data.get("total_points", 0),
            "reward_percentage": data.get("reward_percentage", 0),
            "spot_reward_percentage": data.get("spot_reward_percentage", 0),
            "raw": data
        }
    return None


# -------------------------
# 🔹 PROTOCOLS CONFIG
# -------------------------
protocols = {
    "🟣 Ethena": lambda w: get_ethena(w),
    "🟣 Hylo": lambda w: get_hylo(w),
    "🟣 Level": lambda w: get_level(w),
    "🟣 Noon": lambda w: get_noon(w),
    "🟣 Kyros": lambda w: get_kyros(w),
    "🟣 Triad": lambda w: get_triad(w),
    "🟣 Kinetiq": lambda w: get_kinetiq(w),
    "🟣 Hyperbeat": lambda w: get_hyperbeat(w),
    "🟣 RateX": lambda w: get_ratex(w),
    "🟣 Ranger": lambda w: get_ranger(w),
}

# -------------------------
# 🔹 INPUT
# -------------------------
wallet = st.text_input("Digite sua carteira (0x...)", value="0x2A78c88C4012544D11E41736505B8D67abBA0532")

if wallet:
    tabs = st.tabs(list(protocols.keys()))

    for i, (name, fetch_func) in enumerate(protocols.items()):
        with tabs[i]:
            data = fetch_func(wallet)
            if data:

                # ---- layouts específicos ----
                if name == "🟣 Ethena":
                    col1, col2, col3 = st.columns(3)
                    col1.metric("🔮 Total Shards", f"{data.get('accumulatedTotalShardsEarned', 0):,.0f}")
                    col2.metric("📊 Ethena Shards", f"{data.get('accumulatedEthenaShards', 0):,.0f}")
                    col3.metric("💎 Pendle Shards", f"{data.get('accumulatedPendleShards', 0):,.0f}")

                    col4, col5, col6 = st.columns(3)
                    col4.metric("🌱 Restaking", f"{data.get('accumulatedRestakingShards', 0):,.0f}")
                    col5.metric("🚀 Boost", f"{data.get('accumulatedBoostShards', 0):,.0f}")
                    col6.metric("🌐 L2", f"{data.get('accumulatedL2Shards', 0):,.0f}")

                    st.subheader("🎯 Protocol Points")
                    st.write(
                        f"Derive: **{data.get('accumDerivePts', 0):,.0f}** | "
                        f"Echelon: **{data.get('accumEchelonPts', 0):,.0f}** | "
                        f"Ethereal: **{data.get('accumEtherealPts', 0):,.0f}** | "
                        f"Terminal: **{data.get('accumTerminalPts', 0):,.0f}** | "
                        f"Strata: **{data.get('accumStrataPts', 0):,.0f}**"
                    )

                elif name == "🟣 Level":
                    lb = data.get("leaderboard", [{}])[0].get("balance", {})
                    total_xp = int(lb.get("accrued", 0))
                    referral_xp = int(lb.get("fromReferrals", 0))
                    rank = data.get("rank", "N/A")

                    st.metric("🌟 Total XP", f"{total_xp:,}")
                    st.metric("🏆 Global Rank", rank)
                    st.metric("👥 Referral XP", f"{referral_xp:,}")
                
                elif name == "🟣 Noon":
                    st.metric("🌟 Total Points", f"{data['totalPoints']:,.2f}")
                    st.metric("⏱️ Last 24h", f"{data['last24h']:,.2f}")
                    st.metric("🔗 USN Protocol Total", f"{data['usn_total']:,.2f}")

                elif name == "🟣 Hylo":
                    st.metric("🌟 Total Points", f"{data.get('totalPoints', 0):,.2f}")
                    st.metric("🏆 Global Rank", data.get("globalRank", "N/A"))
                    st.metric("👥 Referral Points", f"{data.get('referralPoints', 0):,.2f}")

                elif name == "🟣 Kyros":
                    st.metric("🌟 Total Points", f"{data['points']:,.2f}")
                    st.metric("🏆 Global Rank", data['rank'])
                    st.metric("👥 Referral Points", f"{data['referralPoints']:,.2f}")

                elif name == "🟣 Triad":
                    st.metric("🌟 Total Points", f"{data['points']:,.2f}")
                    st.metric("🏆 Global Rank", data['rank'])
                    st.metric("👥 Referral Points", f"{data['referralPoints']:,.2f}")
                    st.metric("🔹 TRD Staked", f"{data['trdStaked']:,}")
                
                elif name == "🟣 Kinetiq":
                    st.metric("🌟 Total Points", f"{data.get('points', 0):,.0f}")
                    st.metric("⭐ Tier", data.get("tier", "N/A"))

                elif name == "🟣 Hyperbeat":
                    try:
                        hyperbeat = next((p for p in data["details"] if p["name"] == "Hyperbeat"), None)
                        st.metric("🌟 Hyperbeat Points", f"{float(hyperbeat['balance']):,.2f}")
                        # 2) Criar tabela com os demais
                        others = [p for p in data["details"] if p["name"] != "Hyperbeat"]
                        if others:
                            df = pd.DataFrame(others)
                            df = df[["name", "symbol", "balance", "usdValue", "description"]]  # colunas principais
                            st.subheader("Outros Projetos")
                            st.dataframe(df, use_container_width=True)
                    except:
                        st.warning("⚠️ No data to this Wallet!")
                
                elif name == "🟣 Perena":
                    st.metric("🌟 Total Points", f"{data['total']:,.2f}")

                    col1, col2, col3 = st.columns(3)
                    col1.metric("🔥 Season 0 Points", f"{data['season0'].get('totalPoints', 0):,.2f}")
                    col2.metric("🏆 Rank", data['season0'].get("rank", "N/A"))
                    col3.metric("📊 Swap Volume", f"{data['season0'].get('totalSwapVolume', 0):,.2f}")

                    col4, col5, col6 = st.columns(3)
                    col4.metric("🔥 Preseason 1 Points", f"{data['preseason1'].get('totalPoints', 0):,.2f}")
                    col5.metric("🏆 Rank", data['preseason1'].get("rank", "N/A"))
                    col6.metric("📊 Swap Volume", f"{data['preseason1'].get('totalSwapVolume', 0):,.2f}")

                    # Detalhes dos protocolos (defiPoints)
                    defi_points = data['preseason1'].get("defiPoints", [])
                    if defi_points:
                        df = pd.DataFrame(defi_points)
                        st.subheader("DeFi Points")
                        st.dataframe(df, use_container_width=True)
                
                elif name == "🟣 RateX":
                    st.metric("🌟 Total Points", f"{data['total_points']:,.2f}")
                    st.metric("💧 LP Points", f"{data['lp_points']:,.2f}")
                    st.metric("💹 Trade Points", f"{data['trade_points']:,.2f}")
                    st.metric("👥 KOL Points", f"{data['kol_points']:,.2f}")
                    st.metric("🎯 Earn Points", f"{data['earn_points']:,.2f}")
                    st.metric("🚀 Boost", f"{data['boost']:,.2f}")
                    st.metric("🏆 Global Rank", data['ranking'])
                    st.write(f"⚙️ Gear: **{data['gear_text']}**")

                elif name == "🟣 Ranger":
                    st.metric("🌟 Total Points", f"{data['total_points']:,.2f}") 
                    st.metric("⭐ Spot Points", f"{data['spot_points']:,.2f}")
                    st.metric("⭐ Perps Points", f"{data['perps_points']:,.2f}")  
                    st.metric("📊 Total Volume", f"{data['total_volume']:,.2f}")
                    st.metric("💹 Spot Volume", f"{data['spot_volume']:,.2f}")
                    st.metric("📈 Perps Volume", f"{data['perps_volume']:,.2f}")                
                    st.metric("🎯 Reward %", f"{data['reward_percentage']}%")
                    st.metric("🎯 Spot Reward %", f"{data['spot_reward_percentage']}%")


                else:
                    st.json(data)

                with st.expander("📄 JSON Bruto"):
                    st.json(data)
            else:
                st.warning(f"⚠️ Não foi possível carregar dados de {name}.")

                with st.expander("📄 JSON Bruto"):
                    st.json(data)
