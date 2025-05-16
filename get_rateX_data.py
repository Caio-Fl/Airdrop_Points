def get_rateX_data(protocol):
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
    if protocol == "kyros":
        qS = 16 #kySOL_querySymbol = 15
        qT = 22 #kySOL_queryTrade = 20
    else:
        qS = 22 #ragSOL_querySymbol = 21
        qT = 23 #fragSOL_queryTrade = 21
    payload = {"serverName": "AdminSvr", "method": "querySymbol", "content": {"cid": "4c00d4ca-b0e8-ebc8-da27-0ac0120b470a"}}#{"serverName":"TradeFRAGSOLSvr","method":"dc.trade.dprice","content":{"cid":"e59573e8-3c48-163d-4a11-902b566b0e20"}}
    url = f"https://api.rate-x.io/"
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    rateXInfoarray = data.get("data", {}).get("symbols", [{}])
    protocolMult = rateXInfoarray[qS].get("partners_reward_boost", {})
    Multiplier = float(protocolMult.split(';')[0])
    symbol = rateXInfoarray[qS].get("symbol_level1_category", {})
    due_date = rateXInfoarray[qS].get("due_date", {})
    base_date = datetime.strptime(due_date.split()[0], '%Y-%m-%d')
    adjusted_date = base_date + timedelta(days=1)
    final_date = adjusted_date.replace(hour=0, minute=0, second=0, microsecond=0)
    expiry =  final_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    tradeFee = float(rateXInfoarray[qS].get("trade_commission", {}))
    priceImpact = 0

    #fragAsUSD = rateXInfoarray.get("14", {})
    payload = {"serverName":"MDSvr","method":"queryTrade","content":{"cid":"f2443b24-44dd-fded-6dba-7a6c567b4ff5"}}
    response2 = requests.post(url, json=payload, headers=headers)
    data2 = response2.json()
    rateXfragarray = data2.get("data", {})
    ytMul = 1/float(rateXfragarray[qT].get("SettlePrice", {}))

    return(ytMul,Multiplier,expiry,tradeFee,priceImpact,final_date,symbol)
