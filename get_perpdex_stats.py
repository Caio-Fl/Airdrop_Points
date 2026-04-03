import requests
from typing import Dict, Optional, Any

def get_perpdex_stats(perpdex: str) -> Dict[str, Optional[Any]]:
    """
    Função que busca dados estatísticos de uma perpetual DEX (perpdex) no DefiLlama.
    
    Parâmetro:
        perpdex (str): Nome da perpdex (ex: "edgex", "hyperliquid", etc.).
    
    Retorna um dicionário com:
        - volume_24h: Volume de trades em 24h (perpVolume.total24h)
        - volume_7d: Volume de trades em 7 dias (perpVolume.total7d)
        - open_interest: Open Interest atual (openInterest.total24h)
        - latest_tvl: Último TVL registrado na matriz "TVL" (último valor do chart)
        - latest_fees: Última fees registrada na matriz "fees" (último valor do chart)
    """
    
    # URL base fornecida por você (basta trocar o nome da perpdex)
    url = f"https://defillama.com/_next/data/m8gPp5vBbyJkD7WrorHIL/protocol/{perpdex}.json?tvl=true&events=false&perpVolume=true"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Levanta erro se não for 200 OK
        data = response.json()
        
        # Acessa a seção principal dos dados
        page_props = data.get("pageProps", {})
        
        # ========================
        # VOLUME 24H e 7D
        # ========================
        perp_volume = page_props.get("perpVolume", {})
        volume_24h = perp_volume.get("total24h")
        volume_7d = perp_volume.get("total7d")
        
        # ========================
        # OPEN INTEREST
        # ========================
        open_interest_data = page_props.get("openInterest", {})
        open_interest = open_interest_data.get("total24h")
        
        # ========================
        # ÚLTIMO TVL (matriz "TVL")
        # ========================
        charts = page_props.get("initialMultiSeriesChartData", {})
        tvl_chart = charts.get("TVL", [])
        latest_tvl = tvl_chart[-1][1] if tvl_chart else None  # Último valor do array [timestamp, valor]
        
        # ========================
        # ÚLTIMA FEES (matriz "fees")
        # ========================
        fees_chart = charts.get("Fees", [])
        latest_fees = fees_chart[-1][1] if fees_chart else None  # Último valor do array [timestamp, valor]
        
        return {
            "perpdex": perpdex,
            "volume_24h": volume_24h,
            "volume_7d": volume_7d,
            "open_interest": open_interest,
            "latest_tvl": latest_tvl,
            "latest_fees": latest_fees,
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro ao buscar dados: {str(e)}"}
    except (KeyError, IndexError, TypeError) as e:
        return {"error": f"Erro ao processar JSON: {str(e)} (verifique se a perpdex existe)"}

