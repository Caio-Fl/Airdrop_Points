def get_rateX_data():
    # Importar Bibliotecas Python
    import requests
    import json
    import time
    from datetime import datetime, timezone, timedelta

    headers = {
            "path": "/",
            "Content-Type": "application/json",
            "Accept": "*/*"
    }

    payload = {"serverName":"AdminSvr","method":"querySymbol","content":{"cid":"ec0aace6-3a68-43c0-895a-0410e3a68310"}} #{"serverName":"TradeFRAGSOLSvr","method":"dc.trade.dprice","content":{"cid":"e59573e8-3c48-163d-4a11-902b566b0e20"}}
    url = f"https://api.rate-x.io/"
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    rateXInfoarray = data.get("data", {}).get("symbols", [{}])
    protocolMult = rateXInfoarray[21].get("partners_reward_boost", {})
    fragMultiplier = float(protocolMult.split(';')[0])
    due_date = rateXInfoarray[21].get("due_date", {})
    base_date = datetime.strptime(due_date.split()[0], '%Y-%m-%d')
    adjusted_date = base_date + timedelta(days=1)
    final_date = adjusted_date.replace(hour=0, minute=0, second=0, microsecond=0)
    expiry =  final_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    tradeFee = float(rateXInfoarray[21].get("trade_commission", {}))
    priceImpact = 0

    #fragAsUSD = rateXInfoarray.get("14", {})
    payload = {"serverName":"MDSvr","method":"queryTrade","content":{"cid":"9f3439e8-53de-da67-09e2-6e168d288ff6"}}
    response2 = requests.post(url, json=payload, headers=headers)
    data2 = response2.json()
    rateXfragarray = data2.get("data", {})
    ytMul = 1/float(rateXfragarray[22].get("SettlePrice", {}))

    return(ytMul,fragMultiplier,expiry,tradeFee,priceImpact,final_date)